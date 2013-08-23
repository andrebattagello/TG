import cloud
import pprint


def get_job_stats(job_id):
    info = cloud.info(job_id, ["stdout", "stderr", "logging", "runtime", "status"])
    job_stats = info[job_id]

    print "Job ID: ", job_id
    print "Job Runtime: ", job_stats["runtime"]
    print "Job Status: ", job_stats["status"]

    if job_stats["stdout"]:
        print "[Job STDOUT]"
        print "------------"
        pprint.pprint(job_stats["stdout"])

    if job_stats["stderr"]:
        print "[Job STDERR]"
        print "------------"
        pprint.pprint(job_stats["stderr"])

    if job_stats["logging"]:
        print "[Job LOGGING]"
        print "------------"
        pprint.pprint(job_stats["logging"])
