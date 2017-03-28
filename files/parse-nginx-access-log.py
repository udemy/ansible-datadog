import re, sys, datetime, time

def parselog(logger,line):
    #for lb101 or lb102
    reg1 = re.compile('.+(?:\d+\.\d+\.\d+\.\d+):(?:(?:\d+\.\d+\.\d+\.\d+)|(?:-)).+\[(.+?) .+] (?:[\d.]+) ([\d.]+) .+(?:PUT|GET|POST|HEAD|PATCH|DELETE|OPTIONS|TRACE|DEBUG) (.+?)(?:\?| HTTP).+?1" (?:\d+).+?"(?:.+?)".+u:(?:-|\d+) v:(?:-|\d+)')

    # group values:
    m_datetime = 1
    m_elapsed = m_datetime + 1
    m_path = m_elapsed + 1

    mats = reg1.search(line)
    if not mats:
        return None
    
    #Parse DateTime
    t_datetime = datetime.datetime.strptime(mats.group(m_datetime), "%d/%b/%Y:%H:%M:%S")
    t_datetime = int(time.mktime(t_datetime.timetuple()))

    #final format of path
    t_path = re.sub(r'\d\d+','#',mats.group(m_path))
    
    t_attributes = {'Destination Page':t_path}
    t_time_taken = float(mats.group(m_elapsed))
    
    t_metric_name = "nginx_log_load_times_per_path"

    return (t_metric_name,t_datetime,t_time_taken,t_attributes)
