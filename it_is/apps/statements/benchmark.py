import timeit

print "SQL:"
timer = timeit.Timer("utils.test_sql()", "from apps.statements import utils")
sql_res = min(timer.repeat(repeat=3, number=10000))
print sql_res

print "List:"
timer = timeit.Timer("utils.test_list()", "from apps.statements import utils")
list_res = min(timer.repeat(repeat=3, number=10000))
print list_res

print "Diff:"
print sql_res/list_res