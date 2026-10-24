# AI Engineer Interview Questions — Full Practice Bank

Total: 59 questions across 10 topics. Basics first, then subject questions, difficulty increasing.
Use it like this: read a question, answer out loud in your own words, then check the sample answer.

## Python

### Basic questions

1. **Variable ante enti? Python lo x = 10 ante em jaruguthundi?**
   - Sample answer: A variable is a named reference to a value stored in memory; x = 10 binds the name x to the integer object 10.

2. **List ki tuple ki difference enti?**
   - Sample answer: Lists are mutable and can be changed after creation; tuples are immutable and fixed.

### Subject questions

3. **Function ante enti? def enduku use chestam?**
   - Sample answer: A function is a reusable block of code defined with def; it takes parameters, does work, and can return a value.

4. **OOP lo class ki object ki difference enti?**
   - Sample answer: A class is a blueprint; an object is a concrete instance created from that blueprint.

5. **Decorator ante enti? Oka example ivvandi.**
   - Sample answer: A decorator is a function that takes another function and returns a wrapped version with extra behaviour, applied with @ syntax.

6. **Exception handling lo try-except enduku use chestam?**
   - Sample answer: try-except catches runtime errors so the program can recover instead of crashing.

7. **Generator ante enti? List tho difference enti?**
   - Sample answer: A generator yields values one at a time with yield, using little memory, unlike a list which stores everything.

## SQL

### Basic questions

8. **SQL ante enti? Database lo enduku use chestam?**
   - Sample answer: SQL is the language used to query and manage data stored in a relational database.

9. **SELECT statement em chestundi?**
   - Sample answer: SELECT retrieves chosen columns and rows from a table.

### Subject questions

10. **WHERE ki HAVING ki difference enti?**
   - Sample answer: WHERE filters rows before grouping; HAVING filters groups after GROUP BY.

11. **INNER JOIN ki LEFT JOIN ki difference enti?**
   - Sample answer: INNER JOIN returns only matching rows from both tables; LEFT JOIN returns all left-table rows plus matches.

12. **GROUP BY ante enti?**
   - Sample answer: GROUP BY groups rows sharing a value so aggregate functions like COUNT or SUM apply per group.

13. **Subquery ante enti?**
   - Sample answer: A subquery is a query nested inside another query, whose result feeds the outer query.

14. **Window function oka example ivvandi.**
   - Sample answer: Window functions like ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) compute values across a set of rows related to the current row.

## Mathematics for AI

### Basic questions

15. **Average (mean) ante enti? Ela calculate chestam?**
   - Sample answer: The mean is the sum of values divided by how many values there are.

16. **Probability ante enti simple ga cheppandi.**
   - Sample answer: Probability is the likelihood of an event, measured between 0 (impossible) and 1 (certain).

### Subject questions

17. **Vector ante enti? ML lo enduku important?**
   - Sample answer: A vector is an ordered list of numbers with magnitude and direction; in ML it represents features or embeddings.

18. **Derivative ante enti?**
   - Sample answer: A derivative measures how fast a function's output changes when its input changes — the slope at a point.

19. **Gradient ante enti? Gradient descent lo ela use avuthundi?**
   - Sample answer: The gradient points in the direction of steepest increase; gradient descent steps opposite to it to minimize loss.

20. **Matrix multiplication eppudu possible?**
   - Sample answer: Matrix multiplication is possible when the first matrix's column count equals the second matrix's row count.

## Machine Learning

### Basic questions

21. **Machine Learning ante enti simple ga?**
   - Sample answer: Machine learning lets computers learn patterns from data and make predictions on new data.

22. **Training data ante enti?**
   - Sample answer: Training data is the example data a model learns from.

### Subject questions

23. **Overfitting ante enti? Ela reduce chestaru?**
   - Sample answer: Overfitting is memorising training data and failing on new data; reduce it with more data, regularization, simpler models and cross-validation.

24. **Regression ki classification ki difference enti?**
   - Sample answer: Regression predicts a continuous number; classification predicts a category or class.

25. **Accuracy saripothunda? Precision, recall eppudu chudali?**
   - Sample answer: Accuracy can mislead on imbalanced data; precision and recall show the cost of false positives and false negatives.

26. **Regularization ante enti?**
   - Sample answer: Regularization adds a penalty on large weights to keep the model simpler and reduce overfitting.

## Deep Learning

### Basic questions

27. **Neural network ante enti simple ga?**
   - Sample answer: A neural network is layers of connected neurons with weights that adjust during learning.

28. **Activation function enduku kavali?**
   - Sample answer: Activation functions add non-linearity so the network can learn complex patterns.

### Subject questions

29. **Backpropagation ante enti?**
   - Sample answer: Backpropagation computes the gradient of the loss for each weight using the chain rule, so weights can be updated.

30. **CNN enduku images ki best?**
   - Sample answer: CNNs use convolution filters that detect local features like edges while respecting the spatial structure of images.

31. **Transformer lo attention ante enti?**
   - Sample answer: Attention lets each token weigh which other tokens are most relevant to it when building its representation.

32. **Optimizer em chestadu? Adam ki SGD ki difference?**
   - Sample answer: An optimizer updates weights using gradients; Adam adapts the learning rate per parameter, while plain SGD uses one rate for all.

## Generative AI

### Basic questions

33. **Tokenization ante enti? LLM ki enduku important?**
   - Sample answer: Tokenization splits text into tokens from a fixed vocabulary; each token maps to an ID the model embeds and processes.

34. **LLM ante enti?**
   - Sample answer: An LLM is a large language model trained on huge text data to predict and generate text.

### Subject questions

35. **Embeddings ante enti?**
   - Sample answer: Embeddings are dense vectors that capture meaning, so similar ideas sit close together in vector space.

36. **RAG ante enti? Eppudu use chestaru?**
   - Sample answer: RAG retrieves relevant documents, adds them as context, and grounds the LLM answer in that evidence.

37. **Prompt engineering lo manchi prompt ela rayali?**
   - Sample answer: A good prompt is clear and specific, gives context, states the output format, and includes examples when needed.

38. **Vector database enduku use chestam?**
   - Sample answer: A vector database stores embeddings and performs fast similarity (nearest-neighbour) search over them.

## AI Agents

### Basic questions

39. **AI agent ante enti? Chatbot tho difference enti?**
   - Sample answer: An agent uses an LLM plus tools to take multi-step actions toward a goal, not just reply with text like a basic chatbot.

40. **Tool calling ante enti?**
   - Sample answer: Tool calling lets the model choose an external function/API and supply its arguments in a structured format.

### Subject questions

41. **Agent memory enduku important?**
   - Sample answer: Memory lets an agent remember previous steps and state so multi-step tasks stay coherent.

42. **Guardrails ante enti agents lo?**
   - Sample answer: Guardrails constrain agent actions — allowed tools, checked inputs/outputs, and human approval for risky steps.

43. **Agent ni ela evaluate chestaru?**
   - Sample answer: Evaluate agents by task completion rate, correctness of tool calls, cost/latency, and human review of outcomes.

## MLOps

### Basic questions

44. **Deployment ante enti?**
   - Sample answer: Deployment means putting the application on a server so real users can access it.

45. **API ante enti simple ga?**
   - Sample answer: An API is an interface through which two programs request and respond to each other.

### Subject questions

46. **FastAPI enduku ML services ki popular?**
   - Sample answer: FastAPI is popular for ML services because it is fast, async, validates data with Pydantic, and auto-generates API docs.

47. **Docker ante enti? Container enduku use chestam?**
   - Sample answer: Docker packages an app with its environment into a container that runs the same everywhere.

48. **Model monitoring enduku kavali deployment tarvata?**
   - Sample answer: Monitoring detects data drift and performance drops after deployment so the model can be retrained or fixed.

49. **CI/CD ante enti?**
   - Sample answer: CI/CD automatically tests and deploys code changes through a pipeline whenever code is pushed.

## Coding Interviews

### Basic questions

50. **List lo unna numbers anni kalipithe output enti? numbers = [10, 20, 30]**
   - Sample answer: sum([10, 20, 30]) is 60.

51. **Loop ante enti?**
   - Sample answer: A loop repeats a block of code — for repeats over items, while repeats while a condition is true.

### Subject questions

52. **String palindrome aa kaada ela check chestaru?**
   - Sample answer: Compare the string with its reverse (s == s[::-1]) or use two pointers from both ends.

53. **Dictionary lo word frequency ela count chestaru?**
   - Sample answer: Iterate words, using a dictionary to store and increment each word's count (d.get(w, 0) + 1).

54. **Bug unna code ni debugging ela start chestaru?**
   - Sample answer: First reproduce the bug, read the error, then isolate with prints/tests step by step until the failing line is found.

## HR Interviews

### Basic questions

55. **Meeru me gurinchi cheppandi — self-introduction ela start chestaru?**
   - Sample answer: Start with your name, background, key skills with one example, and the role you are aiming for — in about one minute.

56. **Mee strength enti? Example tho cheppandi.**
   - Sample answer: Name one real strength and prove it with a short example of what you did and its result.

### Subject questions

57. **Ee project ni interviewer ki ela explain chestaru?**
   - Sample answer: Explain the problem, your solution, your specific role, the tools used, and the measurable result.

58. **Mee weakness enti ani adigithe ela answer cheyyali?**
   - Sample answer: Be honest about a real weakness and describe the concrete steps you are taking to improve it, with progress.

59. **Team lo disagreement vaste ela handle chestaru?**
   - Sample answer: Listen first, discuss the trade-offs respectfully, and decide based on the team's shared goal.
