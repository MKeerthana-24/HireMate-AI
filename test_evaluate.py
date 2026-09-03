from ai import evaluate_answer

question = "What is the difference between List and Tuple?"

answer = """
List is mutable.
Tuple is immutable.
List uses [].
Tuple uses ().
"""

result = evaluate_answer(question, answer)

print(result)