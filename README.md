# Backend Project: Searching Tweets
## Approach to the problems:
- [x] Optimization  
1. The original code splits the tweet by spaces and saves the splited words into a list, and then check if the word we want is in the list.  
**Line 40-45 in starter_code:**
``` python
words_in_tweet = tweet.split(" ")
tweet_contains_query = True
for word in list_of_words:
    if word not in words_in_tweet:
      tweet_contains_query = False
      break
```
This checking would be time consuming if the tweet is large, for example, having more than million words in one tweets. This is because that checking if an element is in the list in python is of O(n) time complexity. We could revise this by using a set to store the splited words, which reduces the avarage time complexity to O(1) in the same checking. Also, considering that converting the whole tweet to lower case every time we visit it would be costly, we transfer the tweets into lower case at the first time when we read the file.  
**Line 186-188 in myCode:**
``` python
lowercase_tweets = set()
for word in tweet.split():
lowercase_tweets.add(word.lower())
```
2. The original code always checks all the elements in the tweet stock to get the tweet with the largest timestamp.  
**Line 39-47 in starter_code:**
``` python
for tweet, timestamp in self.list_of_tweets:
    words_in_tweet = tweet.split(" ")
    tweet_contains_query = True
        for word in list_of_words:
            if word not in words_in_tweet:
                tweet_contains_query = False
                break
        if tweet_contains_query and timestamp > result_timestamp:
            result_tweet, result_timestamp = tweet, timestamp
```
If the file of tweet set is very large, the running time would be expectedly large. We could simply sort the tweets according to their timestamp and start searching from the tweet with the largest timestamp. In this case, once we meet the tweet containing the word we want, we could immediately return.  
**Line 154-158 in myCode:**
``` python
for row in list_of_timestamps_and_tweets:
    timestamp = int(row[0])
    tweet = row[1]
    self.list_of_tweets.append((tweet, timestamp))
self.list_of_tweets.sort(key = lambda x:x[1], reverse = True)
```
***
- [x] Return 5 tweets  
I create a loop of 5 searches. In each loop, I delete the returned elements in the tweets set to remove the duplicates.  
**Line 196-206 in myCode:**
``` python
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
```
***
- [x] Handle logic operators  
The point of solving this problem is similar to building an SQL parser and a visitor. I first define the TreeNode type, build up an AST following the grammer rules, and then build the returned tweet list inorder. One treenode represents one expression. The TreeNode.type saves the operator type('!', '|', '&'). A TreeNode with self.type == 'w' stores a word, which means that the expression is a word; otherwise, the expression is one of the operations. The notleft and notright parameters reveal if the node's left child or right child is a 'not' node. They are f the convenience of the visitor.
**Line 5-1 in myCode:**
``` python
class TreeNode:
    def __init__(self, Type = None, left=None, right=None, notword=None, Notleft=False, Notright = False):
        self.type = Type
        self.left = left
        self.right = right
        self.notleft = Notleft
        self.notright = Notright
```

## How to run:
> python myCode.py  

To test different cases, modify the str cmd at line 191. The generated AST and the result would be automatically printed.

## Further analysis:
The code consists of 2 main parts: the parser and the visitor.  
The logistic of the visitor is simple: starting from the root node, check the node type and do corresponding operations. After that, visit its children and do the same things in the recursion. At the leaves of the tree, the nodes are of type 'w', and we call 'search' function to search the tweets with the largest timestamp tweets. The tweets are then assembled on the higher level of the recursion. AST traversal time complexity is always O(n).  
The parser constructs the AST. I first split the words with the operators. For those words sticked with the parenthesis and 'not' sign ('!'), I do additionally process to split them.  
**Line 66-77 in myCode:**
``` python
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
```
The nested loops here looks troublesome and complex, but the number of parenthesis and 'not' sign ('!') are not expected to be extremely large compared to the length of query. We don't have to worry about the time complexity in this part.
After that, I declare 2 stacks for operators and expressions each. I iterator over the list of the operators and the words splited before. Every time we meet an operator or a word, I push the operator to the op_stack or a treenode of 'w' type with the word to the exp_stack. For every parenthesis pairs, I treat the elements in between as an expression, and create a treenode for each of them. Whenever a right parenthesis is visited, I pop all the operators from the stack until a left parenthesis is visited. Every time an operator is popped, 2 expressions are popped for 'and' ('&') or 'or' ('|') operator, and 1 expression is popped for 'not' ('!') operation; then, the popped expression(s), along with the popped operator, is used to construct a treenode, which is pushed to the expression stack after born.  
At last, if there are still multiple operators left in the op_stack (they must be parallel 'and' ('&') or 'not' ('!') operators in this case), I did same thing as though they are expressions at different level, but their hierarchy does not matter as long as we traverse the tree in Inorder.  
Also, the nested loops in the parser function (constructTree) seems time consuming, but they actually are iterating over small ranges, such as the number of parenthesis. Other than nested loops, the loops doing different operations are parallel to each others. Therefore the overall time complexity is O(len(query)).  
A problem of my code is that it is not space-friendly. I not only create 2 copies of the tweets dataset, but also call numerous functions with lists as parameters, which could be a burden for the stack. If I would have more time on the project, I will try to find the solution to save more spaces from the search.
