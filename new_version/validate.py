from schema import Schema, Optional, And, Or, Use

def run_input_validation(config):
    def l(s,name=None):
        s = "lambda {}".format(s)
        ll = eval(s)
        if name is None:
            ll.func_name = s
        else:
            ll.func_name = name
        return ll
    return Schema({
        "species":[
            {
                "switch": And(
                    l("x:isinstance(x,list)","isAList"),
                    l("x:len(x)>0","lengthGreaterThanZero"),
                    l("x:(False not in [isinstance(a,list) for a in x])","allEntriesAreLists"),
                    l("x:(False not in [len(a)==len(x[0]) for a in x])","allEntriesHaveSameSize"),
                    Schema([[0,1]]),
                    l("x:(False not in [sum([a[i] for a in x])>0 for i in range(len(x[0]))])","allColumnsHaveAtLeastOne")),
                "choice": And(
                    l("x:isinstance(x,list)","isAList"),
                    l("x:len(x)>0","lengthGreaterThanZero"),
                    l("x:(False not in [isinstance(a,list) for a in x])","allEntriesAreLists"),
                    l("x:(False not in [len(a)==len(x[0]) for a in x])","allEntriesHaveSameSize"),
                    Schema([[int,float,basestring]]))
            }
        ],
        Optional("range_substitutions"):[
            And(list,
            l("x:len(x)==2","hasLengthTwo"),
            l("x:isinstance(x[0],basestring)","firstElementIsString"),
            l("x:isinstance(x[1],dict)","secondElementIsDict"),
            Schema([basestring,{
                "min":Use(float),
                "max":Use(float),
                Optional("step"):Use(float)
            }]))
        ],
        Optional("range_constraints"):[
            And(basestring)
        ],
        "output":basestring,
        "max_iterations":And(int,l("x:x>1","greaterThanOne")),
        "convergence_sample_size":And(int,l("x:x>1","greaterThanOne")),
        "convergence_sd":And(Use(float),l("x:x>0","greaterThanZero")),
        "smoothing":And(float, l("x:(x<1 and x>0)","betweenZeroAndOne")),
        Optional("row_pruning", default=False):bool,
        Optional("col_pruning", default=False):bool,
        Optional("write_delay", default=10.0):float,
        Optional("scooped", default=False):bool
    }, ignore_extra_keys=True).validate(config)
