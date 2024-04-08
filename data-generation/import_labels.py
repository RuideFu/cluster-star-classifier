import json

import sqlalchemy as sa
from sqlalchemy.sql import text
import sqlalchemy.orm as orm

DB_BACKEND = "mysql+pymysql"
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = ""


def main():
    # create engine and session
    db_uri = '{}://{}:{}@{}:{}/{}'.format(DB_BACKEND, DB_USER, DB_PASS, DB_HOST, DB_PORT, "astronomicon")
    engine = sa.create_engine(db_uri)
    session = orm.scoped_session(orm.sessionmaker())
    session.configure(bind=engine)
    # query the database, get all observations
    obs_list = session.execute(
        text("SELECT cluster_id, ra, `dec`, score, constraints FROM astronomicon_submission")).all()
    # parse constraints of each observation
    parsed_obs_list = []
    for obs in obs_list:
        cluster_id, ra, dec, score, constraints = obs
        constraints = json.loads(constraints)
        distance_range = (constraints["distance"]["min"], constraints["distance"]["max"])
        pm_ra_range = (constraints["pm_ra"]["min"], constraints["pm_ra"]["max"])
        pm_dec_range = (constraints["pm_dec"]["min"], constraints["pm_dec"]["max"])
        parsed_obs_list.append(
            {"cluster_id": cluster_id, "ra": ra, "dec": dec, "score": score, "distance_range": distance_range,
             "pm_ra_range": pm_ra_range, "pm_dec_range": pm_dec_range})

    # remove duplicates
    parsed_obs_list.sort(
        key=lambda x: x["cluster_id"] * 10 - x["score"])  # sort by cluster_id with score as a tiebreaker
    unique_obs_list = []
    for obs in parsed_obs_list:
        if len(unique_obs_list) == 0 or unique_obs_list[-1]["cluster_id"] != obs["cluster_id"]:
            unique_obs_list.append(obs)
            print(unique_obs_list[-1])
    print(len(unique_obs_list))


if __name__ == '__main__':
    main()
