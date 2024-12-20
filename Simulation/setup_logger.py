import logging

"""
This python file is used to log the attacks and retrieve the data in order to conduct experiments and plot meaningful graphs.
"""


logging.basicConfig(level=logging.DEBUG,
                    filename="attack_logs/attack_log.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')

logger = logging.getLogger("TEC_logger")

