AWS EC2 Instance

# Activate crosscompute virtualenv
export WORKON_HOME=$HOME/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
workon crosscompute



TODO:
[ ] Save results
[ ] Pass default parameters to functions:
    [ ] number of users in simulation
    [ ] evaluation ratio
    [ ] number of users to recommend
    [ ] read from JSON data


Roadmap / Next steps:
=====================
[ ] Implement baseline results: part I (popularity)
[ ] Baseline results - part II (artists similarity)


Useful links
============
- Amazon Elastic MapReduce using MrJob Python library
  http://musicmachinery.com/2011/09/04/how-to-process-a-million-songs-in-20-minutes/

- Examples using the technique above (data from S3):
  https://github.com/echonest/msd-examples

- https://github.com/johnnywalleye/million_song_challenge


Songs mismatching
=================
http://labrosa.ee.columbia.edu/millionsong/blog/12-1-2-matching-errors-taste-profile-and-msd


PiCloud useful commands:
========================
List all dirs in my data volume:
picloud exec -v dataset-volume ls / | xargs picloud result


Recommender Systems in Python
=============================

https://github.com/ocelma/python-recsys
http://ocelma.net/software/python-recsys/build/html/


Metrics
=======

https://github.com/benhamner/Metrics/tree/master/Python/ml_metrics
    - Mean Average Precision

Additional Metrics
(see "The Million Song Dataset Challenge.pdf", pages 4-5)
(see also https://github.com/ocelma/python-recsys/blob/master/doc/source/evaluation.rst)
(https://github.com/ocelma/python-recsys/blob/master/recsys/evaluation/ranking.py)
    - Mean Reciprocal Rank (MRR)
    - Normalized Discounted Cumulative Gain (nDCG)
    - Precision at 10 (P10)
    - Recall at the Cutoff (R_tau)
