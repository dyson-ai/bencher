from bencher.plugins import Base

if __name__ == "__main__":
    for p in Base.plugins:
        inst = p()
        inst.start()
