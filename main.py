from sqlalchemy import create_engine, select, ForeignKey, Column, Table, and_  
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship, Session

class Base(DeclarativeBase):
    pass



class Track(Base):
    __tablename__ = "track"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    genre: Mapped[str] = mapped_column() 

    album_id: Mapped[str] = mapped_column(ForeignKey("album.id")) 
    album: Mapped["Album"] = relationship(back_populates="tracks")

    musician_id: Mapped[str] = mapped_column(ForeignKey("musician.id")) 
    musician: Mapped["Musician"] = relationship(back_populates="tracks")




class Album(Base):

    __tablename__ = "album"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    tracks: Mapped[list["Track"]] = relationship(back_populates="album")

    musician_id: Mapped[int] = mapped_column(ForeignKey("musician.id"))
    musician: Mapped["Musician"] = relationship(back_populates="albums")




class Musician(Base):

    __tablename__ = "musician"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    tracks: Mapped[list["Track"]] = relationship(back_populates="musician")

    albums: Mapped[list["Album"]] = relationship(back_populates="musician")




def add_musician(Session: sessionmaker):
    with Session() as session:
        name = input("\nВведите имя музыканта: ")
        stmt = select(Musician).where(Musician.name == name)
        musician = session.scalars(stmt).first()
        if musician is not None:
            print("\nЭтот музыкант уже есть в системе")
            return
        else:
            new_musician: Musician = Musician(name=name)
            session.add(new_musician)
            session.commit()
            stmt = select(Musician).where(Musician.name == name)
            musician = session.scalars(stmt).first()
            if musician is not None:
                print(f"\nМузыкант {musician.name} успешно добавлен")

def add_album(Session: sessionmaker):
    with Session() as session:

        attention = input('\nОбратите внимание, что если во время добавления альбома вы укажите несуществующего музыканта, произойдет ошибка и введенные данные не сохранятся.\nВведите 1, чтобы продолжить, или 2, чтобы вернуться назад\n')
        if attention == '2':
            start_menu(Session)

        album_name = input("\nВведите название альбома: ")
        musician_name = input("Введите имя музыканта: ")

        musician_stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(musician_stmt).first()

        if musician is not None:
            for album in musician.albums:
                if album.name == album_name:
                    print(f"\nАльбом {album.name} музыканта {musician.name} уже есть в системе")
                    return

            new_album: Album = Album(name=album_name, musician_id=musician.id, musician=musician)
            session.add(new_album)
            session.commit()

            stmt = select(Album).where(Album.name == new_album.name)
            album = session.scalars(stmt).first()

            if album is not None:
                print(f"\nАльбом {album.name} музыканта {musician.name} успешно добавлен")

def add_track(Session: sessionmaker):
    with Session() as session:
        
        attention = input('\nОбратите внимание, что если во время добавления трека вы укажите несуществующего музыканта или несуществующий альбом, произойдет ошибка и введенные данные не сохранятся.\nВведите 1, чтобы продолжить, или 2, чтобы вернуться назад\n')
        if attention == '2':
            start_menu(Session)

        name: str = input("\nВведите название трека: ")
        genre: str = input("Введите жанр трека: ")
        musician_name: str = input("Введите имя музыканта: ")
        album_name: str = input("Введите название альбома: ")

        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()

        stmt = select(Album).where(Album.name == album_name, Album.musician == musician)
        album = session.scalars(stmt).first()

        if album is not None:
            # есть ли ранее созданный трек с:
            stmt = select(Track).where(and_(Track.name == name, Track.genre == genre, Track.album == album, Track.musician == musician))
            
            track = session.scalars(stmt).first()
            
            if track is None:
                new_track: Track = Track(name=name, genre=genre, album_id=album.id, album=album, musician=album.musician, musician_id=album.musician.id)
                session.add(new_track)
                session.commit()
                
                stmt = select(Track).where(Track.name == name)
                track = session.scalars(stmt).first()

                if track is not None:
                    print(f"\nТрек {track.name} альбома {album.name} музыканта {album.musician.name} успешно добавлен")
            
            else:
                print("такй трек уже есть")
                print(f"\nТрек {track.name} альбома {album.name} музыканта {album.musician.name} уже есть в системе")
                return


def show_all_tracks(Session: sessionmaker):
    with Session() as session:
        stmt = select(Musician)
        musicians = session.scalars(stmt).all()
        for musician in musicians:
            for album in musician.albums:
                for track in album.tracks:
                    print(f"\nId: {track.id}\nНазвание трека: {track.name}\nМузыкант: {musician.name}\nАльбом: {album.name}\nЖанр: {track.genre}\n")

def musicians(Session: sessionmaker):
    with Session() as session:
        stmt = select(Musician)
        musicians = session.scalars(stmt).all()
        for i in range(len(musicians)):
            print(f"{i+1}. {musicians[i].name}")

def find_musician_tracks(Session: sessionmaker):
    musician_name = input("\nВведите имя музыканта: ")
    with Session() as session:
        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()
        if len(musician.tracks) > 0:
            print(f"\nУ музыканта {musician.name} есть следующие треки: ")
            for i in range(len(musician.tracks)):
                print(f"{i+1}. {musician.tracks[i].name}")
        else:
            print(f"\nУ музыканта {musician.name} пока что нет добавленных треков")

def find_genre_tracks(Session: sessionmaker):
    genre_name = input("\nВведите жанр: ")
    with Session() as session:
        stmt = select(Track).where(Track.genre == genre_name)
        tracks = session.scalars(stmt).all()
        if len(tracks) > 0:
            print(f"\nВ жанре {genre_name} написаны следующие треки: ")
            for i in range(len(tracks)):
                print(f"{i+1}. {tracks[i].name}")
        else:
            print(f"\nВ жанре {genre_name} пока что нет добавленных треков")

def find_musician_albums(Session: sessionmaker):
    name = input("\nВведите имя музыканта: ")
    with Session() as session:
        stmt = select(Musician).where(Musician.name == name)
        musician = session.scalars(stmt).first()
        if len(musician.albums) > 0:
            print(f"\nУ музыканта {musician.name} есть следующие альбомы: ")
            for i in range(len(musician.albums)):
                print(f"{i+1}. {musician.albums[i].name}")
        else:
            print(f"\nУ музыканта {musician.name} пока что нет добавленных альбомов")

def find_musician_album_tracks(Session: sessionmaker):
    musician_name = input("\nВведите имя музыканта: ")
    album_name = input("Введите название альбома: ")
    album = None

    with Session() as session:
        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()
        if musician is not None:

            for a in musician.albums:
                if a.name == album_name:
                    album = a 

            if album is not None:
                if len(album.tracks) > 0:
                    print(f"\nВ альбоме {album_name} музыканта {musician_name} есть следующие треки: ")
                    for i in range(len(album.tracks)):
                        print(f"{i+1}. {album.tracks[i].name}")
                else:
                    print(f"\nВ альбоме {album_name} музыканта {musician_name} пока что нет добавленных треков")
        else:
            print(f"\nМузыкант {musician_name} не найден")

def update_track(Session: sessionmaker):
    with Session() as session:

        attention = input('\nОбратите внимание, что если во время изменения данных о треке вы укажите несуществующего музыканта или несуществующий альбом, произойдет ошибка и введенные данные не сохранятся.\nВведите 1, чтобы продолжить, или 2, чтобы вернуться назад\n')
        if attention == '2':
            start_menu(Session)

        musician_name: str = input("\nВведите имя музыканта: ")
        album_name: str = input("Введите название альбома: ")
        name: str = input("Введите название трека: ")

        stmt = select(Musician).where(and_(Musician.name == musician_name))
        musician = session.scalars(stmt).first()
        album = None

        if musician is not None:
            for a in musician.albums:
                if a.name == album_name:
                    album = a

            if album is not None:
                for t in album.tracks:
                    if t.name == name:
                        track = t

                if track is not None:
                    new_name: str = input("\nВведите новое название трека: ")
                    new_genre: str = input("Введите новый жанр трека: ")
                    new_musician_name: str = input("Введите новое имя музыканта: ")
                    new_album_name: str = input("Введите новое название альбома: ")

                    musician_stmt = select(Musician).where(Musician.name == new_musician_name)
                    new_musician = session.scalars(musician_stmt).first()
                    stmt = select(Album).where(Album.name == new_album_name)
                    new_album = session.scalars(stmt).first()

                    if new_musician is not None:
                        if new_album is not None:
                            track.name=new_name
                            track.genre=new_genre
                            track.album_id=new_album.id
                            track.album=new_album
                            track.musician=new_musician
                            track.musician_id=new_musician.id
                            session.commit()

                            stmt = select(Track).where(and_(Track.genre == new_genre, Track.album_id == new_album.id, Track.album == new_album, Track.musician == new_musician, Track.musician_id == new_musician.id))
                            track = session.scalars(stmt).first()
                            if track is not None:
                                print(f"\nТрек {track.name} альбома {track.album.name} музыканта {track.musician.name} успешно обновлен")
                        else:
                            print(f"Новый альбом {new_album_name} не найден")
                    else:
                        print(f"Новый музыкант {new_musician_name} не найден")
                else:
                    print(f"\nТрек для изменения {name} альбома {album_name} музыканта {musician_name} не найден")
            else:
                print(f"Альбом {album_name} не найден")
        else:
            print(f"Музыкант {musician_name} не найден")


def update_album(Session: sessionmaker):
    with Session() as session:

        attention = input('\nОбратите внимание, что если во время изменения данных об альбоме вы укажите несуществующего музыканта, произойдет ошибка и введенные данные не сохранятся.\nВведите 1, чтобы продолжить, или 2, чтобы вернуться назад\n')
        if attention == '2':
            start_menu(Session)

        musician_name = input("\nВведите имя музыканта: ")
        album_name = input("Введите название альбома: ")
        album = None
        
        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()

        if musician is not None:
            # если музыкант существует

            for a in musician.albums:
                if a.name == album_name:
                    album = a
            # находим альбом

            if album is not None:
                # если найденный альбом существует
                new_album_name = input("\nВведите новое название альбома: ")
                new_musician_name = input("Введите новое имя музыканта: ")

                stmt = select(Musician).where(Musician.name == new_musician_name)
                new_musician = session.scalars(stmt).first()

                if new_musician is not None:

                    album.name=new_album_name
                    album.musician_id=new_musician.id
                    album.musician=new_musician
                    
                    if album.musician == new_musician:
                        session.commit()

                    stmt = select(Album).where(Album.name == new_album_name)
                    album = session.scalars(stmt).first()

                    if album is not None:
                        print(f"\nАльбом {album.name} музыканта {album.musician.name} успешно обновлен")
                else:
                    print(f"Музыкант {new_musician_name} не найден")
            else:
                print(f"\nАльбом {album_name} музыканта {musician_name} не найден")
        else:
            print(f"Музыкант {musician_name} не найден")

def update_musician(Session: sessionmaker):
    with Session() as session:
        name = input("\nВведите имя музыканта: ")
        stmt = select(Musician).where(Musician.name == name)
        musician = session.scalars(stmt).first()

        if musician is not None:
            new_name = input("\nВведите новое имя музыканта: ")
            stmt = select(Musician).where(Musician.name == new_name)
            new_musician = session.scalars(stmt).first()
            
            if new_musician is None:

                musician.name = new_name
                session.commit()

                if musician.name == new_name:
                    print(f"\nМузыкант {musician.name} успешно обновлен")
            else:
                print(f"\nМузыкант с именем {new_name} уже есть в системе")
        else:
            print(f"\nМузыкант {musician.name} не найден")


def delete_track(Session: sessionmaker):
    with Session() as session:

        track_name: str = input("\nВведите название трека: ")
        album_name: str = input("Введите название альбома: ")
        musician_name: str = input("Введите имя музыканта: ")
        
        stmt = select(Musician).where(and_(Musician.name == musician_name))
        musician = session.scalars(stmt).first()
        album = None
        track = None

        if musician is not None:
            for a in musician.albums:
                if a.name == album_name:
                    album = a

            if album is not None:
                for t in album.tracks:
                    if t.name == track_name:
                        track = t

                if track is not None:
                    session.delete(track)
                    session.commit()
                    print(f"Трек {track_name} успешно удален")

                else:
                    print(f"\nТрек {track_name} не найден")
            else:
                print(f"\nАльбом {album_name} не найден")
        else:
            print(f"\nМузыкант {musician_name} не найден")

def delete_album(Session: sessionmaker):
    with Session() as session:
        album = None

        album_name: str = input("\nВведите название альбома: ")
        musician_name: str = input("Введите имя музыканта: ")

        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()

        if musician is not None:
            for a in musician.albums:
                if a.name == album_name:
                    album = a

            if album is not None:
                for track in album.tracks:
                    session.delete(track)
                session.delete(album)
                session.commit()
                print(f"Альбом {album_name} успешно удален")
                
            else:
                print(f"\nАльбом {album_name} не найден")
        else:
            print(f"\nМузыкант {musician_name} не найден")

def delete_musician(Session: sessionmaker):
    with Session() as session:

        musician_name: str = input("\nВведите имя музыканта: ")
        
        stmt = select(Musician).where(Musician.name == musician_name)
        musician = session.scalars(stmt).first()

        if musician is not None:

            for album in musician.albums:
                for track in album.tracks:
                    session.delete(track)
                session.delete(album)
            session.delete(musician)
            session.commit()

            stmt = select(Musician).where(Musician.name == musician_name)
            musician = session.scalars(stmt).first()

            if musician is None:
                print(f"\nМузыкант {musician_name} успешно удален")

        else:
            print(f"\nМузыкант {musician_name} не найден")




def main():
    engine = create_engine("sqlite:///m_c.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    while 1:
        start_menu(Session)
        exit()



def start_menu(Session):
    menu = """\n\n1. Добавить
2. Посмотреть
3. Изменить
4. Удалить
5. Выход\n
Выберите команду: """

    uc = input(menu)
    if uc == '1':
        add_menu_func(Session)
        start_menu(Session)

    elif uc == '2':
        show_menu_func(Session)
        start_menu(Session)
    
    elif uc == '3':
        update_menu_func(Session)
        start_menu(Session)
    
    elif uc == '4':
        delete_menu_func(Session)
        start_menu(Session)

    elif uc == '5':
        exit()

def add_menu_func(Session):
    add_menu = """\n\n1. Добавить трек
2. Добавить альбом
3. Добавить музыканта
4. Назад\n
Выберите команду: """

    uc = input(add_menu)
    if uc == '1':
        add_track(Session)
        start_menu(Session)

    elif uc == '2':
        add_album(Session)
        start_menu(Session)
    
    elif uc == '3':
        add_musician(Session)
        start_menu(Session)

    elif uc == '4':
        start_menu(Session)

def show_menu_func(Session):
    show_menu = """\n\n1. Посмотреть все треки
2. Посмотреть всех музыкантов
3. Посмотреть все треки музыканта
4. Посмотреть все треки жанра
5. Посмотреть все альбомы музыканта
6. Посмотреть все треки альбома музыканта
7. Назад\n
Выберите команду: """

    uc = input(show_menu)
    if uc == '1':
        show_all_tracks(Session)
        start_menu(Session)

    elif uc == '2':
        musicians(Session)
        start_menu(Session)
    
    elif uc == '3':
        find_musician_tracks(Session)
        start_menu(Session)

    elif uc == '4':
        find_genre_tracks(Session)
        start_menu(Session)
    
    elif uc == '5':
        find_musician_albums(Session)
        start_menu(Session)

    elif uc == '6':
        find_musician_album_tracks(Session)
        start_menu(Session)

    elif uc == '7':
        start_menu(Session)

def update_menu_func(Session):
    update_menu = """\n\n1. Изменить данные о треке
2. Изменить данные об альбоме
3. Изменить данные о музыканте
4. Назад\n
Выберите команду: """

    uc = input(update_menu)
    if uc == '1':
        update_track(Session)
        start_menu(Session)

    elif uc == '2':
        update_album(Session)
        start_menu(Session)
    
    elif uc == '3':
        update_musician(Session)
        start_menu(Session)

    elif uc == '4':
        start_menu(Session)

def delete_menu_func(Session):
    delete_menu = """\n\n1. Удалить трек
2. Удалить альбом
3. Удалить музыканта
4. Назад\n
Выберите команду: """

    uc = input(delete_menu)
    if uc == '1':
        delete_track(Session)
        start_menu(Session)

    elif uc == '2':
        delete_album(Session)
        start_menu(Session)
    
    elif uc == '3':
        delete_musician(Session)
        start_menu(Session)

    elif uc == '4':
        start_menu(Session)


if __name__ == "__main__":
    main()
