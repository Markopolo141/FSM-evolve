window.sim = {}

window.sim.log_simulation = true

window.sim.zip = (a1, a2) ->
    if a1.length != a2.length
        return false
    ret = []
    for a, i in a1
        ret.push([a, a2[i]])
    return ret

window.sim.zip_dict = (a1, a2) ->
    z = sim.zip(a1, a2)
    if z
        ret = {}
        for a in z
            ret[a[0]] = a[1]
        return ret
    else
        return false

window.sim.array_multiply = (a, n) ->
    z = []
    if n > 0
        range = [0..(n-1)]
        for aa in range
            for b in a
                z.push(b)
    return z

window.sim.identity_function = (x) ->
    return x

window.sim.abs_sum = (X) ->
    s = 0
    X.forEach (n) ->
        s = s + math.abs(n)
    return s

window.sim.delta = (a) ->
    return if a==0 then 1.0 else 0.0

window.sim.displace = (a, b, proportion) ->
    return math.add(a, math.multiply(proportion, math.subtract(b, a)))

window.sim.manhattan_distance = (a,b,sub=math.subtract) ->
    return sim.abs_sum(sub(b, a))

window.sim.manhattan_normalize = (a,mul=math.multiply) ->
    s = math.sum(a)
    s = sim.delta(s) + s
    return mul((1.0/s), a)

window.sim.generate_even_vector = (size) ->
    a = 1.0/size
    return math.matrix(sim.array_multiply([[a]], size))

window.sim.generate_constant_vector = (size, val) ->
    return math.matrix(sim.array_multiply([[val]], size))

window.sim.matrix_len = (m) ->
    s = m.size()
    return s[0] * s[1]
    
window.sim.get_max = (list) ->
    return math.max([-Infinity].concat(list))

window.sim.get_max_index = (obj_list, func=sim.identity_function) ->
    f = -Infinity
    index = undefined
    for o in obj_list
        funced_val = func(o)
        if funced_val > f
            f = funced_val
            index = _i
    return index

window.sim.get_max_of = (obj_list, func=sim.identity_function) ->
    f = -Infinity
    obj = undefined
    for o in obj_list
        funced_val = func(o)
        if funced_val > f
            f = funced_val
            obj = o
    return obj

window.sim.is_ergodic = (m, n=5, err=0.000001) ->
    size = m.size()
    if size[0] != size[1]
        return false
    syms = []
    m.forEach (v) ->
        syms = syms.concat(sim.get_symbols(sim.safe_parse(v)))
    syms = (s for s in syms when s not in _results)
    for i in [0..n]
        vals = []
        for s in syms
            vals.push(math.random()*90-45)
        symbol_scope = sim.zip_dict(syms, vals)
        mm = m.clone()
        for row, row_index in mm._data
            for element, col_index in row
                mm._data[row_index][col_index] = sim.safe_eval(element, symbol_scope)
        mul = 1
        while (mul < size[1])
            mm = math.add(math.multiply(mm,mm), mm)
            mul = mul * 2
        is_no_zeros = true
        mm.forEach (() -> (v) ->
            if math.abs(v) <= err
                is_no_zeros = false).apply(this)
        if is_no_zeros == false
            return false
    return true

window.sim.get_symbols = (v) ->
    v_symbols = []
    if v.traverse
        v.traverse (n) ->
            if n.isSymbolNode
                v_symbols.push(n.name)
    v_symbols = (s for s in v_symbols when s not in _results)
    return v_symbols

window.sim.is_expression_with = (v, atoms) ->
    for sym in sim.get_symbols(v)
        if sym not in atoms
            return false
    return true
    
window.sim.matrix_is_expressions_with = (m, atoms) ->
    ret = true
    m.forEach (() -> (v) ->
        if not sim.is_expression_with(sim.safe_parse(v), atoms)
            ret = false).apply(this)
    return ret

window.sim.check_expression_positive_semi_definite = (m, refinement=3) ->
    syms = []
    m.traverse (a) ->
        if a.isSymbolNode and a not in syms
            syms.push(a.name)
    f = (dim)->
        if dim > 0
            ret = []
            for i in (q/refinement for q in [0..(refinement)])
                for z in f(dim-1)
                    ret.push([i].concat(z))
            return ret
        else
            return [[]]
    
    for nums in f(syms.length)
        if m.eval(sim.zip_dict(syms, nums)) < 0
            return false
    return true

window.sim.check_matrix_positive_semi_definite = (m, refinement) ->
    ret = true
    m.forEach (() -> (v) ->
        if sim.check_expression_positive_semi_definite(sim.safe_parse(v), refinement) == false
            ret = false).apply(this)
    return ret

window.sim.variable_translate = (nums) ->
    t = [1.0]
    nums.forEach (() -> (n) ->
        t.push(t[t.length-1]*n/(1.0-n))
        ).apply(this)
    t_sum = math.sum(t)
    return (a/t_sum for a in t)

window.sim.distributed_variable_translate = (dist, nums) ->
    parsed_nums = []
    nums.forEach (n) ->
        parsed_nums.push(n)
    r = []
    i = 0
    for d in dist
        if d>0
            r.push(sim.variable_translate(parsed_nums.slice(i, i+d)))
        else
            r.push(undefined)
        i = i + d
    return r

window.sim.get_distribution = (m) ->
    dist = (math.sum(c) for c in math.transpose(m).toArray())
    return ((if d>1 then d-1 else 0) for d in dist)

pop_dict = {}
window.sim.weight_choice = (choice, pop) ->
    pop_size = pop.size()
    choice_size = choice.size()
    if pop_size[0] * pop_size[1] != Object.keys(pop_dict).length
        pop_dict = {}
    i = 0
    pop.forEach (p) ->
        pop_dict["s"+i] = p
        i = i + 1
    weighted_choice = math.matrix(math.zeros(choice_size[0], choice_size[1]))
    for row, row_index in choice._data
        for element, col_index in row
            weighted_choice._data[row_index][col_index] = sim.safe_parse(element).eval(pop_dict)
    return weighted_choice

window.sim.weight_switch = (switch_table, nums, dist=undefined) ->
    if dist == undefined
        dist = sim.get_distribution(switch_table)
    weighted_switch = switch_table.clone()
    distributed = sim.distributed_variable_translate(dist, nums)
    for col_index in [0..(switch_table.size()[1]-1)]
        if distributed[col_index]
            for row_index in [0..(switch_table.size()[0]-1)]
                if switch_table.get([row_index, col_index])
                    weighted_switch._data[row_index][col_index] = distributed[col_index].pop()
    return weighted_switch

window.sim.safe_parse = (a) ->
    if typeof a != 'object'
        return math.parse(a)
    return a

window.sim.safe_eval = (a, scope) ->
    if typeof a['eval'] == 'undefined'
        return math.eval(a, scope)
    else
        return a.eval(scope)

window.sim.parse_matrix = (m) ->
    for c, ci in m._data
        for r, ri in c
            m._data[ci][ri] = sim.safe_parse(r)
    return m
    
window.sim.expanded_multiply = (A, B) ->
    if typeof A != 'object'
        A = math.parse(A)
    if typeof B != 'object'
        B = math.parse(B)
    Z = math.parse("A*B")
    Z.args = [A,B]
    return Z

window.sim.expanded_sum = (s) ->
    s.reduce (previousValue, currentValue, index, array) ->
        Z = math.parse("A+B")
        Z.args = [previousValue, currentValue]
        return Z

window.sim.symbol_matrix_multiply = (A, B) ->
    Asize = A.size()
    Bsize = B.size()
    if (Asize[0] != Bsize[1]) or (Asize[1] != Bsize[0])
        throw "symbol_matrix_multiply dimensions are wrong"
    get_row = (A, r) ->
        return A._data[r]
    get_col = (A, c) ->
        return (d[c] for d in A._data)
    C = math.zeros(Asize[0], Bsize[1])
    for r in [0..(Asize[0]-1)]
        for c in [0..(Bsize[1]-1)]
            row = get_row(A, r)
            col = get_col(B, c)
            C._data[r][c] = sim.expanded_sum((sim.expanded_multiply(row[i], col[i]) for z,i in row))
    return C

window.sim.check_input = (switch_table, choice_table) ->
    switch_size = switch_table.size()
    choice_size = choice_table.size()
    if not (switch_size[0] == choice_size[1] and switch_size[1] == choice_size[0])
        return false
    choice_table = choice_table.clone()
    m = sim.symbol_matrix_multiply(sim.parse_matrix(choice_table), switch_table)
    if not sim.matrix_is_expressions_with(m, ("s"+i for i in [0..(switch_table.size()[1]-1)]))
        return false
    if not sim.is_ergodic(m)
        return false
    if not sim.check_matrix_positive_semi_definite(m)
        return false
    return true

class Simulation
    iterate: ->
        throw "NotImplementedError"
    getQuality: ->
        throw "NotImplementedError"
    getTrait: ->
        throw "NotImplementedError"
    getData: ->
        throw "NotImplementedError"
    simulate_from_dict: (d) ->
        @simulate(d['target_quality'], d['target_trait_change'], d['repeated'], d['min_iterations'], d['max_iterations'])
    simulate: (target_quality=Infinity, target_trait_change=Infinity, repeated=0, min_iterations=1, max_iterations=1000) ->
        if sim.log_simulation
            @log_message("Beginning iteration: Arguments = #{JSON.stringify(arguments)}")
        iteration = 0
        old_trait = -Infinity
        repeats = 0
        while iteration < max_iterations
            iteration = iteration + 1
            @iterate()
            new_trait = @getTrait()
            if sim.log_simulation
                @log_message("Iteration #{iteration} - trait: #{new_trait}, trait_change: #{new_trait-old_trait}, quality: #{@getQuality()}")
            if @getQuality() <= target_quality and math.abs(new_trait-old_trait) <= target_trait_change
                if iteration >= min_iterations
                    repeats = repeats + 1
                    if repeats > repeated
                        return iteration
            else
                repeats = 0
            old_trait = new_trait
        console.log("WARNING, SIMULATE REACHED MAX ITERATIONS")
        return iteration
    log_message: (item, arr_name="messages") ->
        if sim.log_simulation
            if @log[arr_name]
                @log[arr_name] = @log[arr_name].concat([item])
            else
                @log[arr_name] = [item]
window.sim.Simulation = Simulation

class SubPopulationGrowthSimulation extends Simulation
    constructor: (weighted_switch, weighted_choice, config, @log) ->
        @smoothing_factor = config['smoothing_factor']
        if not @smoothing_factor > 0 and @smoothing_factor < 1
            throw "smoothing factor needs to between >0 and <1"
        @multiplier_matrix = math.multiply(weighted_choice, weighted_switch)
        @population = sim.generate_even_vector(math.transpose(weighted_switch)._data.length)
        if sim.log_simulation
            @log_message("SubPopulation growth sim")
            @log_message("weighted_switch - #{weighted_switch.toString()}")
            @log_message("weighted_choice - #{weighted_choice.toString()}")
            @log_message("config - #{JSON.stringify(config)}")
            @log_message("multiplier_matrix - #{@multiplier_matrix}")
            @log_message("initial population - #{@population}")
    iterate: ->
        @old_population = @population
        @population = sim.displace(@old_population, math.multiply(@multiplier_matrix, @population), @smoothing_factor)
        @growth_factor = math.sum(@population)
        @population = sim.manhattan_normalize(@population)
        @change_factor = sim.manhattan_distance(@population, @old_population)
        if sim.log_simulation
            @log_message(@population.toArray(), "population")
            @log_message(@growth_factor, "growth")
        return @population
    getQuality: ->
        return @change_factor
    getTrait: ->
        return @growth_factor
    getData: ->
        return @population
window.sim.SubPopulationGrowthSimulation = SubPopulationGrowthSimulation

class EnsembleSimulation extends Simulation
    constructor: (@sims, @log) ->
        if sim.log_simulation
            @log_message("Ensemble Simulation")
            @log_message("#{@sims.length} sims")
    iterate: ->
        for s in @sims
            s.iterate()
    getTrait: ->
        return sim.get_max((s.getTrait() for s in @sims))
    getQuality: ->
        return sim.get_max_of(@sims, (x) -> x.getTrait() ).getQuality()
    getData: ->
        return sim.get_max_of(@sims, (x) -> x.getTrait() ).getData()
window.sim.EnsembleSimulation = EnsembleSimulation

sim_number_generator = (nums, mutation_shift) ->
    r = []
    for i in [0..(sim.matrix_len(nums)-1)]
        r.push(nums.clone())
        r[r.length-1]._data[i][0] = sim.displace(r[r.length-1]._data[i][0], 1, mutation_shift)
        r.push(nums.clone())
        r[r.length-1]._data[i][0] = sim.displace(r[r.length-1]._data[i][0], 0, mutation_shift)
    return r

class MutateSimulation extends Simulation
    constructor: (@switch_table, @choice_table, @config, @log) ->
        @switch_dist = sim.get_distribution(switch_table)
        num_dim = math.sum(@switch_dist)
        if num_dim == 0
            throw "there are no choices to simulate over..."
        @log.subs = []
        if sim.log_simulation
            @log_message("NEW MUTATION SIM")
            @log_message("switch_table : #{@switch_table.toString()}")
            @log_message("choice_table : #{@choice_table.toString()}")
            @log_message("config : #{JSON.stringify(@config)}")
            @log_message("switch_distribution : #{@switch_dist}")
            @log_message("num_dim : #{num_dim}")
        @newer = sim.generate_constant_vector(num_dim, 0.5)
        @newer_pre_func = sim.weight_choice(@choice_table, sim.generate_even_vector(@switch_table.size()[1]))
        @newer_obj = @func([@newer], @newer_pre_func)[0]
        @newer_value = @newer_obj.getTrait()
        @mutation_shift = @config['mutation_incorporation_factor']
    func: (nums, pre) ->
        sub_log = {subs:[]}
        if sim.log_simulation
            @log.subs = @log.subs.concat([sub_log])
        ensemble_sims = []
        for n, i in nums
            sub_log.subs = sub_log.subs.concat([{}])
            weighted_switch = sim.weight_switch(@switch_table, n, @switch_dist)
            ensemble_sims.push(new SubPopulationGrowthSimulation(weighted_switch, pre, @config['SubPopulationGrowthSimulation'], sub_log.subs[i]))
        ensemble = new EnsembleSimulation(ensemble_sims, sub_log)
        ensemble.simulate_from_dict(@config['simulate_params'])
        return ensemble.sims
    iterate: ->
        @older = @newer
        @older_obj = @newer_obj
        @older_pre_func = @newer_pre_func
        @older_value = @newer_value
        points = sim_number_generator(@newer,@config['mutation_shift'])
        objs = @func(points, @newer_pre_func)
        values = (o.getTrait() for o in objs)
        index = sim.get_max_index(values)
        if values[index] > @newer_value
            @newer = sim.displace(@older, points[index], @mutation_shift)
            @newer_obj = @func([@newer], @newer_pre_func)[0]
            @newer_pre_func = sim.weight_choice(@choice_table, sim.displace(@older_obj.population, @newer_obj.population, @config['incorporation_factor']))
            @newer_value = @newer_obj.getTrait()
            if sim.log_simulation
                @log_message(@newer.toArray(), "genetics")
                @log_message(@newer_value, "growth_rate")
                @log_message(@newer_pre_func.toArray(), "weighted_choice")
                @log_message(@newer_obj.population.toArray(), "population")
                @log_message(sim.weight_switch(@switch_table, @newer, @switch_dist).toArray(), "weighted_switch")
    getQuality: ->
        return sim.manhattan_distance(@older, @newer)
    getTrait: ->
        return @newer_value
    getData: ->
        return [@newer, @newer_obj]
window.sim.MutateSimulation = MutateSimulation

class EvolveSimulation extends Simulation
    constructor: (@switch_table, @choice_table, @config, @log) ->
        @log.subs = [{}]
        if sim.log_simulation
            @log_message("NEW EVOLUTION SIM")
            @log_message("switch_table : #{@switch_table.toString()}")
            @log_message("choice_table : #{@choice_table.toString()}")
            @log_message("config : #{JSON.stringify(@config)}")
        @choice_table = sim.parse_matrix(@choice_table)
        if not sim.check_input(switch_table, choice_table)
            throw "assert input check fail"
        @simulation = new MutateSimulation(@switch_table, @choice_table, @config['MutateSimulation'], @log.subs[0])
        @reduction = @config['initial_reduction']
        @new_trait = -Infinity
    iterate: ->
        @old_trait = @new_trait
        @simulation.muation_shift = @reduction
        if sim.log_simulation
            @log.subs = @log.subs.concat([{subs:[]}])
            @simulation.log = @log.subs[@log.subs.length-1]
            @log_message("Altering mutation-shift to: #{@reduction}")
        @simulation.simulate_from_dict(@config['simulate_params'])
        @new_trait = @simulation.getTrait()
        @reduction = @reduction * @config['reduction_compaction']
    getQuality: ->
        return math.abs(@new_trait - @old_trait)
    getTrait: ->
        return @new_trait
    getData: ->
        return @simulation
        
    getPopulation: ->
        return @simulation.newer_obj.population
    getGrowthRate: ->
        return @simulation.newer_value
    getGenetics: ->
        return @simulation.newer
    getWeightedChoiceTable: ->
        return @simulation.newer_pre_func
    getWeightedSwitchTable: ->
        return sim.weight_switch(@simulation.switch_table, @simulation.newer, @simulation.switch_dist)
window.sim.EvolveSimulation = EvolveSimulation




'''@click.command()
@click.argument('config', type=click.File('r'))
def loadSim(config):
    logger.info("Reading lines from files")
    config_text = config.read()
    config.close()
    logger.info("Translating file text to matricies")
    try:
        config = json.loads(config_text)
    except:
        logger.error("Failed to parse config file as valid JSON")
        raise
    try:
        switch = Matrix.FromString(config['switch'], parser=int)
        choice = Matrix.FromString(config['choice'], parser=parse_expr)
    except:
        logger.error("Failed to parse text to matricies")
        raise
    print "SWITCH-TABLE:\n{}".format(switch)
    print "CHOICE-TABLE:\n{}".format(choice)
    logger.info("Booting Simulation Instance")
    sim = EvolveSimulation(switch, choice, config)
    logger.info("Running Simulation Instance")
    sim.simulate(**config['simulate_params'])
    print "__SIMULATION_END__"
    print "SWITCH-TABLE:\n{}".format(switch)
    print "CHOICE-TABLE:\n{}".format(choice)
    print "FINAL POPULATION\n{}".format(sim.simulation.new_obj.population)
    print "WEIGHTED-SWITCH-TABLE\n{}".format(weight_switch(switch, sim.simulation.new))
if __name__ == '__main__':
    loadSim()'''




