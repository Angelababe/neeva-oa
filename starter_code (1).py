import csv
from typing import List, Tuple
from collections import deque

class TreeNode:
    def __init__(self, Type = None, left=None, right=None, notword=None, Notleft=False, Notright = False):
        self.type = Type
        self.left = left
        self.right = right
        self.notleft = Notleft
        self.notright = Notright

class TweetIndex:
    
    def __init__(self):
        self.list_of_tweets = []
        self.invalid = False
        
    def searchTree(self, node: TreeNode, notlist: list):
        if self.invalid:
            return ("", -1)
        if node.type == '&':
            return self.process_and(node, notlist)
        elif node.type == '|':
            return self.process_or(node, notlist)
        elif node.type == '!':
            return self.process_not(node.left)
        elif node.type == 'w':
            return self.search(node.left, notlist)
        
    def process_not(self, node):
        print(node.left.lower())
        return [node.left.lower()]
    
    def process_or(self, node, notlist):
        leftret = self.searchTree(node.left, notlist)
        rightret = self.searchTree(node.right, notlist)
        if leftret[1] > rightret[1]:
            return leftret
        else:
            return rightret
        
    def process_and(self, node, notlist):
        if node.notleft and not node.notright:
            notlist = self.searchTree(node.left, notlist)
            return self.searchTree(node.right, notlist)
        elif node.notright and not node.notleft:
            notlist = self.searchTree(node.right, notlist)
            return self.searchTree(node.left, notlist)
        elif node.notleft and node.notright:
            notlist = self.searchTree(node.left, notlist)
            tweet, stamp = self.searchTree(node.right, notlist)
            notlist[0] += tweet
            notlist[1] += stamp
            return notlist
        else:
            left = self.searchTree(node.left, [])
            right = self.searchTree(node.right, [])
            return (left[0]+right[0], left[1]+right[1])
            
    def constructTree(self, query:str):
        exp_stack = deque([])
        op_stack = deque([])
        splits = query.split(' ')
        splitsCpy = []
        for i in range(len(splits)):
            while splits[i][0] == '!' or splits[i][0] == '(':
                splitsCpy.append(splits[i][0])
                splits[i] = splits[i][1:]
            
            wordidx = len(splits[i])-1
            while splits[i][wordidx] == ')':
                wordidx-=1
                
            splitsCpy.append(splits[i][:wordidx+1])
            for j in range(len(splits[i]) - 1 - wordidx):
                splitsCpy.append(')')
        
        left_p = 0
        for c in splitsCpy:
            if c == '&':
                op_stack.append(c)
            elif c == '|':
                if op_stack:
                    if op_stack[-1] == '&' or op_stack[-1] == '!':
                        self.invalid = True
                        return
                if not len(splitsCpy) == 3 and not left_p > 0:
                    self.invalid = True
                    return
                op_stack.append(c)
            elif c == '!':
                op_stack.append(c)
            elif c == '(':
                op_stack.append('(')
                left_p += 1
            elif c == ')':
                while not op_stack[-1] == '(':
                    op = op_stack.pop()
                    right = exp_stack.pop()
                    left = exp_stack.pop()
                    temp = TreeNode(op, left, right)
                    if left.type == '!':
                        temp.notleft = True
                    elif right.type == '!':
                        temp.notright = True
                    exp_stack.append(temp)
                op_stack.pop()
                left_p -= 1
            else:
                if op_stack:
                    if not op_stack[-1] == '(':
                        if op_stack[-1] == '!':
                            exp_stack.append(TreeNode(op_stack.pop(), TreeNode('w', c)))
                        else:
                            exp_stack.append(TreeNode(op_stack.pop(), exp_stack.pop(), TreeNode('w', c)))
                    else:
                        exp_stack.append(TreeNode('w', c))
                else:
                    exp_stack.append(TreeNode('w', c))
        
        while op_stack:
            if op_stack[-1] == '!':
                exp_stack.append(TreeNode(op_stack.pop(), exp_stack.pop()))
            else:
                op = op_stack.pop()
                left = exp_stack.pop()
                right = exp_stack.pop()
                temp = TreeNode(op, left, right)
                if left.type == '!':
                    temp.notleft = True
                elif right.type == '!':
                    temp.notright = True
                exp_stack.append(temp)
        return exp_stack[-1]
    
    def search(self, word: str, notlist: list):
        wordlower = word.lower()
        for tweet, timestamp in self.list_of_tweets:
            if wordlower in tweet[0]:
                contain_not_word = False
                if notlist:
                    for notword in notlist[0]:
                        if notword[0] in tweet[0]:
                            contain_not_word = True
                            break
                if contain_not_word:
                    continue
                else:
                    return ([tweet[1]], timestamp)
        return ([], 0)
                
    def process_tweets(self, list_of_timestamps_and_tweets: List[Tuple[str, int]]) -> None:
        for row in list_of_timestamps_and_tweets:
            timestamp = int(row[0])
            tweet = row[1]
            self.list_of_tweets.append((tweet, timestamp))
        self.list_of_tweets.sort(key = lambda x:x[1], reverse = True)
    
    #debug use
    def traverse(self, root, lvl):
        if self.invalid:
            return
        if type(root.left) == str:
            print(lvl, root.left)
            return
        else:
            self.traverse(root.left, lvl+'    ')
        print(lvl, root.type)
        if root.right:
            self.traverse(root.right, lvl+'    ')
    

if __name__ == "__main__":
    # A full list of tweets is available in data/tweets.csv for your use.
    tweet_csv_filename = "../data/tweets.csv"
    list_of_tweets = []
    with open(tweet_csv_filename, "r") as f:
        csv_reader = csv.reader(f, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                # header
                continue
            timestamp = int(row[0])
            tweet = str(row[1])
            lowercase_tweets = set()
            for word in tweet.split():
                lowercase_tweets.add(word.lower())
            list_of_tweets.append((timestamp, (lowercase_tweets, tweet)))
    
    cmd = "(!hello & (yay | neeva)) & me"
    ti = TweetIndex()
    ti.process_tweets(list_of_tweets)
    root = ti.constructTree(cmd)
    ti.traverse(root, " ")
    for i in range(5):
        ret = ti.searchTree(root,[])
        print(ret[0])
        removed = set()
        for r in ret[0]:
            if r in removed:
                break
            for j in range(len(ti.list_of_tweets)):
                if r == ti.list_of_tweets[j][0][1]:
                    removed.add(ti.list_of_tweets.pop(j)[0][1])
                    break