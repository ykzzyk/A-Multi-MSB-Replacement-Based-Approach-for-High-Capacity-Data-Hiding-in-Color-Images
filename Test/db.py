from tinydb import TinyDB, Query

if __name__ == '__main__':
    db = TinyDB('db.json')
    db.insert({'type': 'apple', 'count': 7})

    print(db.all())

    Fruit = Query()
    print(db.search(Fruit.image == 'lena')[-1])

    if db.search(Fruit.image == 'lena')[-1]:
        print('True')
