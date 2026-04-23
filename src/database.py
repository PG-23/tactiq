"""
database.py
Defines the PostgreSQL schema and loads parsed player data.

Setup:
  pip install psycopg2-binary sqlalchemy python-dotenv

Create a .env file:
  DATABASE_URL=postgresql://user:password@localhost:5432/tactiq
"""

import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, ARRAY, text
)
from sqlalchemy.orm import declarative_base, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id            = Column(Integer, primary_key=True, autoincrement=True)

    # Identity
    name          = Column(String, nullable=False, index=True)
    age           = Column(Integer)
    nationality   = Column(String)
    club          = Column(String)
    positions     = Column(ARRAY(String))   # e.g. ['D (C)', 'D (R)']
    value         = Column(Float)           # in £
    wage          = Column(Float)           # per week in £

    # Technical
    corners       = Column(Integer)
    crossing      = Column(Integer)
    dribbling     = Column(Integer)
    finishing     = Column(Integer)
    first_touch   = Column(Integer)
    free_kick     = Column(Integer)
    heading       = Column(Integer)
    long_shots    = Column(Integer)
    long_throws   = Column(Integer)
    marking       = Column(Integer)
    passing       = Column(Integer)
    penalty_taking= Column(Integer)
    tackling      = Column(Integer)
    technique     = Column(Integer)

    # Mental
    aggression    = Column(Integer)
    anticipation  = Column(Integer)
    bravery       = Column(Integer)
    composure     = Column(Integer)
    concentration = Column(Integer)
    decisions     = Column(Integer)
    determination = Column(Integer)
    flair         = Column(Integer)
    leadership    = Column(Integer)
    off_the_ball  = Column(Integer)
    positioning   = Column(Integer)
    teamwork      = Column(Integer)
    vision        = Column(Integer)
    work_rate     = Column(Integer)

    # Physical
    acceleration  = Column(Integer)
    agility       = Column(Integer)
    balance       = Column(Integer)
    jumping_reach = Column(Integer)
    natural_fitness = Column(Integer)
    pace          = Column(Integer)
    stamina       = Column(Integer)
    strength      = Column(Integer)

    # Goalkeeping
    aerial_reach      = Column(Integer)
    command_of_area   = Column(Integer)
    communication     = Column(Integer)
    eccentricity      = Column(Integer)
    handling          = Column(Integer)
    kicking           = Column(Integer)
    one_on_ones       = Column(Integer)
    reflexes          = Column(Integer)
    rushing_out       = Column(Integer)
    tendency_to_punch = Column(Integer)
    throwing          = Column(Integer)

    # Computed score (populated by scoring.py)
    position_score = Column(Float)

    def __repr__(self):
        return f"<Player {self.name} | {self.positions} | Score: {self.position_score}>"


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)
    print("Database tables created.")


def upsert_players(players: list[dict]):
    """
    Insert or update players by name + club (simple dedup strategy).
    Clears the table first for a clean import — adjust if you want incremental loads.
    """
    with Session(engine) as session:
        session.execute(text("TRUNCATE TABLE players RESTART IDENTITY"))
        session.commit()

        objs = []
        for p in players:
            # Map parsed dict keys onto ORM columns
            obj = Player(
                name=p.get("name"),
                age=p.get("age"),
                nationality=p.get("nat") or p.get("nationality"),
                club=p.get("club"),
                positions=p.get("position") or [],
                value=p.get("value"),
                wage=p.get("wage") or p.get("ap_w"),  # FM uses 'Ap/W' for agreed wage
                # Technical
                corners=p.get("cor"),
                crossing=p.get("cro"),
                dribbling=p.get("dri"),
                finishing=p.get("fin"),
                first_touch=p.get("fir"),
                free_kick=p.get("fre"),
                heading=p.get("hea"),
                long_shots=p.get("lon"),
                long_throws=p.get("lth"),
                marking=p.get("mar"),
                passing=p.get("pas"),
                penalty_taking=p.get("pen"),
                tackling=p.get("tck"),
                technique=p.get("tec"),
                # Mental
                aggression=p.get("agg"),
                anticipation=p.get("ant"),
                bravery=p.get("bra"),
                composure=p.get("cmp"),
                concentration=p.get("cnt"),
                decisions=p.get("dec"),
                determination=p.get("det"),
                flair=p.get("fla"),
                leadership=p.get("ldr"),
                off_the_ball=p.get("otb"),
                positioning=p.get("pos"),
                teamwork=p.get("tea"),
                vision=p.get("vis"),
                work_rate=p.get("wor"),
                # Physical
                acceleration=p.get("acc"),
                agility=p.get("agi"),
                balance=p.get("bal"),
                jumping_reach=p.get("jum"),
                natural_fitness=p.get("nat_fit") or p.get("nat"),
                pace=p.get("pac"),
                stamina=p.get("sta"),
                strength=p.get("str"),
                # Goalkeeping
                aerial_reach=p.get("aer"),
                command_of_area=p.get("cmd"),
                communication=p.get("com"),
                eccentricity=p.get("ecc"),
                handling=p.get("han"),
                kicking=p.get("kic"),
                one_on_ones=p.get("ono"),
                reflexes=p.get("ref"),
                rushing_out=p.get("rus"),
                tendency_to_punch=p.get("tro"),
                throwing=p.get("thr"),
            )
            objs.append(obj)

        session.bulk_save_objects(objs)
        session.commit()
        print(f"Inserted {len(objs)} players into database.")


if __name__ == "__main__":
    init_db()