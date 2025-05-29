from sqlalchemy import create_engine, select, ForeignKey, Column, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship, Session 

class Base(DeclarativeBase):
    pass




class Tracks(Base):
    __tablename__ = "trasks"

    # id name album_id genre

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    # tracks with album
    album_id: Mapped[str] = mapped_column(ForeignKey("albums.id")) 
    album: Mapped["Albums"] = relationship(back_populates="album")

    genre: Mapped[str] = mapped_column() 

    # tracks with musicians
    musicians: Mapped[list["Musicians"]] = relationship(secondary="musician_track", back_populates="tracks")




class Albums(Base):

    # id name 
    __tablename__ = "albums"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    # album with tracks 
    tracks: Mapped[list["Tracks"]] = relationship(back_populates="track")

    # albums with musicians
    musicians: Mapped[list["Musicians"]] = relationship(secondary="musician_track", back_populates="albums")




class Musicians(Base):

    # id name 
    __tablename__ = "musicians"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    # musicians with tracks
    tracks: Mapped[list["Tracks"]] = relationship(secondary="musician_track", back_populates="tracks")

    # musicians with albums
    albums: Mapped[list["Albums"]] = relationship(secondary="musician_album", back_populates="albums")







musician_track = Table(
    "musician_track",
    Base.metadata,
    Column("musician_id", ForeignKey("musicians.id"), primary_key=True),
    Column("track_id", ForeignKey("tracks.id"), primary_key=True)
)







def add_mucisian(Session: sessionmaker):
    with Session() as session:
        name = input("\nВведите имя музыканта: ")
        new_musician: Musicians = Musicians(name=name)
        session.add(new_musician)
        session.commit()



def add_album(Session):
    with Session() as session:
        num_musicians = int(input("\nВведите количество музыкантов")) 
        list_musicians = []
        for _ in range(num_musicians):
            musician_name = input("\nВведите имя музыканта: ")
            musician_stmt = select(Musicians).where(Musicians.name == musician_name)
            m = session.scalars(musician_stmt).first()
            if m is not None:
                list_musicians.append(session.scalars(musician_stmt).first())

        name = input("\nВведите название альбома: ")
        new_album: Albums = Albums(name=name, musicians=list_musicians)
        for musician in range(len(list_musicians)):
            musician.albums.append(new_album)
        session.add(new_album)
        session.commit()





def add_track(Session):
    with Session() as session:
        num_musicians = int(input("\nВведите количество музыкантов")) 
        list_musicians = []
        for _ in range(num_musicians):
            musician_name = input("\nВведите имя музыканта: ")
            musician_stmt = select(Musicians).where(Musicians.name == musician_name)
            m = session.scalars(musician_stmt).first()
            if m is not None:
                list_musicians.append(session.scalars(musician_stmt).first())

        num_musicians = int(input("\nВведите количество музыкантов")) 
        list_musicians = []
        for _ in range(num_musicians):
            musician_name = input("\nВведите имя музыканта: ")
            musician_stmt = select(Musicians).where(Musicians.name == musician_name)
            m = session.scalars(musician_stmt).first()
            if m is not None:
                list_musicians.append(session.scalars(musician_stmt).first())

        name = input("\nВведите название трека: ")
        genre: str = input("\nВведите жанр трека: ")
        new_track: Albums = Albums(name=name, genre=genre, musicians=list_musicians)
        for musician in range(len(list_musicians)):
            musician.albums.append(new_track)
        session.add(new_track)
        session.commit()


def main():
    engine = create_engine("sqlite:///music_collection.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    menu = """\n\n1. Добавить трек
2. Добавить альбом
3. Добавить музыканта

5. Посмотреть все треки
6. Посмотреть всех музыкантов
7. Посмотреть все треки музыканта
8. Посмотреть все треки жанра
9. Посмотреть все альбомы музыканта
10. Посмотреть все треки альбома

11. Изменить данные о треке
12. Изменить данные об альбоме
13. Изменить данные о музыканте

15. Удалить трек
16. Удалить музыканта
17. Удалить альбом

18. Выход\n
Выберите команду: """



    while 1:
        uc = input(menu)
        if uc == '1':
            add_track(Session)
        # elif uc == '2':
        #     list_books = show_books(Session)
        #     for book in list_books:
        #         print(f"\nId: {book.id}\nАвтор: {book.author}\nНазвание: {book.title}\nГод издания: {book.year_of_publishing}\n------------------")
        # elif uc == '3':
        #     list_books = get_books(Session)
        #     for book in list_books:
        #         print(f"\nId: {book.id}\nАвтор: {book.author}\nНазвание: {book.title}\nГод издания: {book.year_of_publishing}\n------------------")
        # elif uc == '4':
        #     delete_book(Session)
        # elif uc == '5':
        #     update_book(Session)
        elif uc == '6':
            break