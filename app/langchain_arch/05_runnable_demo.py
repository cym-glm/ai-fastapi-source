

from langchain_core.runnables import RunnableLambda

def add(x: int)-> int:
    return x + 1


def mul(x: int)-> int:
    return x * 2


def main():
    add_runnable = RunnableLambda(add)
    mul_runnable = RunnableLambda(mul)

    chain = add_runnable | mul_runnable
    result = chain.invoke(10)
    print("result:", result)

if __name__ == "__main__":
    main()