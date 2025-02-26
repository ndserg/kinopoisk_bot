from datetime import datetime
from sqlalchemy import ForeignKey, BigInteger, Text, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_histories: Mapped[list["History"]] = relationship(
        "History", back_populates="user", cascade="all, delete-orphan"
    )
    watched_list: Mapped[str] = mapped_column(Text, nullable=True)


class History(Base):
    __tablename__ = "histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    history_params: Mapped[str] = mapped_column(Text, nullable=True)
    film_ids: Mapped[list["Films"]] = relationship(
        back_populates="histrories_vs_films", secondary="films_in_histories"
    )
    user: Mapped["User"] = relationship("User", back_populates="user_histories")
    created_at: Mapped[datetime] = mapped_column(server_default=func.date())


class Films(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(primary_key=True)
    film_data: Mapped[dict] = mapped_column(JSON)
    histrories_vs_films: Mapped[list["History"]] = relationship(
        back_populates="film_ids", secondary="films_in_histories"
    )


class FilmsInHistories(Base):
    __tablename__ = "films_in_histories"

    histrory_id: Mapped[int] = mapped_column(
        ForeignKey("histories.id", ondelete="CASCADE"), primary_key=True
    )
    film_id: Mapped[int] = mapped_column(
        ForeignKey("films.id", ondelete="CASCADE"), primary_key=True
    )
