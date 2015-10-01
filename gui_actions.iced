window.gui_actions = {}

window.gui_actions.addNode = (nodeData, callback) ->
    questions.askString(
        (string) ->
            if utils.getNodesWhere(label:string).length != 0
                alert("node name allready exists")
                return false
            nodeData.label = string
            nodeData.color = "#aaaaaa"
            nodeData.shape = "dot"
            callback(nodeData)
            return true
        () -> callback()
        "Please enter a unique name for the new node"
    )

window.gui_actions.editNode = (nodeData, callback) ->
    questions.askString(
        (string) ->
            nodeData.label = string
            callback(nodeData)
            gui_actions.refresh()
        () -> callback()
        "Please enter a unique name for the node"
    )

window.gui_actions.deleteNode = (datas, callback) ->
    for e in datas.edges
        data.edges.remove(e)
    for n in datas.nodes
        data.nodes.remove(n)
    gui_actions.refresh()
    callback()

window.gui_actions.addEdge = (edgeData, callback) ->
    checked = $("input[name='choices']:checked")
    if checked.length != 1
        questions.notifyConfirm(
            ()->callback()
            "Please select a choice"
        )
    else
        questions.askEquation(
            (string) ->
                choice_id = checked.attr("value")
                edgeData.math = string
                actions.addEdge(
                    {choice_id: choice_id
                    color: $("##{choice_id} .color").val()
                    choice_name: $("##{choice_id} span").text()},
                    edgeData
                )
                gui_actions.refresh()
                callback()
            () -> callback()
            "Please enter expression for this transition"
        )

window.gui_actions.deleteEdge = (datas, callback) ->
    if datas.edges.length != 1
        questions.notifyConfirm(
            ()->callback()
            "Please select a choice"
        )
    questions.askTristate(
        () ->
            actions.removeEdgesFrom(data.edges.get(datas.edges[0]))
            gui_actions.refresh()
            callback()
        () ->
            actions.removeEdgesTo(data.edges.get(datas.edges[0]))
            gui_actions.refresh()
            callback()
        () ->
            callback()
        "Delete Edges..."
        "from Node"
        "to Node"
        "Cancel"
    )

window.gui_actions.changeChoiceName = (id, new_name) ->
    $("#choicepicker ##{id} .choicelabel").show().text(new_name)
    actions.alterChoice({choice_id:id}, {choice_name:new_name})
    $("#choicepicker ##{id} .choicenameinput").hide()
    gui_actions.refresh()

window.gui_actions.addChoice = () ->
    uuid = vis.util.randomUUID()
    rand_color = vis.util.HSVToHex(Math.random(), 0.95, Math.random()*0.3+0.65).slice(1)
    $("#choicepicker").mk(".hid_overflow[width=100%]##{uuid}"
        radio_element = $.mk("input[type=radio][name=choices][value=#{uuid}]")
        span_element = $.mk("span.choicelabel", "NewChoice")
        input_element = $.mk("input.choicenameinput[size=12][style=display:None;]")
        $.mk(".f_right"
            colorselect = $.mk("input.color[size=1][value=#{rand_color}]")
            upbutton = $.mk("button.choiceupbutton", "V")
            deletebutton = $.mk("button.choicedeletebutton", "X")
        )
    )
    jscolor.bind()
    radio_element.click () ->
        gui_actions.refreshSelection(this.value)
    span_element.click () ->
        span_element.hide()
        input_element.val(span_element.text())
            .show()
            .focus()
    input_element.focusout () ->
        gui_actions.changeChoiceName(uuid, input_element.val())
    input_element.keydown (event) ->
        if event.keyCode == 13
            input_element.focusout()
    upbutton.click () ->
        row = upbutton.parent().parent()
        row.next().after(row)
    deletebutton.click () ->
        gui_actions.choiceDelete(uuid)
    colorselect.on "propertychange change input", 
        () ->
            actions.alterChoice({choice_id:uuid}, {color:colorselect.val()})
            gui_actions.refresh()

window.gui_actions.choiceDelete = (id) ->
    name = $("#choicepicker ##{id} .choicelabel").text()
    questions.askConfirm(
        () ->
            actions.removeChoice({choice_id:id})
            $("#choicepicker ##{id}").remove()
        () -> 
        "Confirm delete of: #{name}"
    )

window.gui_actions.refreshSelection = (id) ->
    if not id
        id = $("input[name='choices']:checked").attr('value')
    $("input[name=choices][value=#{id}]").prop('checked', true)
    choice_name = $("##{id} span").text()
    choice_color = $("##{id} .color").val()
    mathtyped = $("#selectionmathtype").prop("checked")
    
    edges = (e for e in data.edges.get() when e.choice_id == id)
    tos = ([data.nodes.get(e.to), e.math] for e in edges)
    tos = (t for t in tos when t[0].label not in (r[0].label for r in _results))
    froms = (data.nodes.get(e.from) for e in edges)
    froms = (f for f in froms when f.label not in (r.label for r in _results))
    
    selectionInfo = $("#selectionInfo").empty().attr("style", "background-image: linear-gradient(white, white), linear-gradient(white, ##{choice_color});")
    selectionInfo.mk("", 
        "States that can make the choice:"
        selectionTable = $.mk("[style=word-break: break-all; text-align:left; margin: 5 0 5 0; padding: 0 0 0 10;]")
    )
    for f in froms
        selectionTable.mk(".hid_overflow[width=100%]"
            "- #{f.label}"
            $.mk(".f_right"
                del_button = $.mk("button"
                    "X"
                )
            )
        )
        del_button.click ()->
            actions.removeEdgesFrom({choice_id: id, from: f.id})
            gui_actions.refresh()
    selectionInfo.mk("", 
        "choice causes transitions to:"
        selectionTable = $.mk("[style=word-break: break-all; text-align:left; margin: 5 0 5 0; padding: 0 0 0 10;]")
    )
    for t in tos
        equation_text = t[1]
        style_display = "block"
        if mathtyped
            equation_text = "`#{equation_text}`"
            style_display = "none"
        selectionTable.mk(".hid_overflow[width=100%]"
            "- #{t[0].label}"
            $.mk(".f_right"
                del_button = $.mk("button"
                    "X"
                )
            )
            equation_div = $.mk("[style=text-align:center;visibility:#{style_display}]", equation_text)
            input_element = $.mk("input.choicenameinput[size=20][style=display:None;]")
        )
        if mathtyped
            MathJax.Hub.Queue(["Typeset",MathJax.Hub,equation_div[0]])
            MathJax.Hub.queue.Push ()->
                equation_div.attr("style", "text-align:center;")
        
        equation_div.click ((equation_div, input_element, t) -> () ->
            equation_div.hide()
            input_element.val(t[1])
                .attr("style", "display:block;")
                .focus())(equation_div, input_element, t)
        input_element.focusout ((t, id, input_element) -> () ->
            actions.alterChoice({to:t[0].id, choice_id:id}, {math:input_element.val()})
            gui_actions.refresh())(t, id, input_element)
        input_element.keydown ((input_element) -> (event) ->
            if event.keyCode == 13
                input_element.focusout())(input_element)
            
        del_button.click ((id, t) -> ()->
            actions.removeEdgesTo({choice_id: id, to: t[0].id})
            gui_actions.refresh())(id, t)

edgeViewBy = "none"
window.gui_actions.refreshField = (view_by) ->
    if view_by
        edgeViewBy = view_by
    if edgeViewBy == "none"
        data.edges.forEach (edge) ->
            edge.label = ""
            data.edges.update(edge)
    else if edgeViewBy == "name"
        data.edges.forEach (edge) ->
            edge.label = edge.choice_name
            data.edges.update(edge)
    else if edgeViewBy == "math"
        data.edges.forEach (edge) ->
            edge.label = edge.math
            data.edges.update(edge)

window.gui_actions.refresh = () ->
    gui_actions.refreshField()
    gui_actions.refreshSelection()

window.gui_actions.getMatricies = () ->
    states = []
    choices = []
    data.nodes.forEach (node) ->
        if node.id not in states
            states.push(node.id)
    data.edges.forEach (edge) ->
        if edge.choice_id not in choices
            choices.push(edge.choice_id)
    switch_table = math.zeros(choices.length, states.length)
    data.edges.forEach (edge) ->
        switch_table._data[choices.indexOf(edge.choice_id)][states.indexOf(edge.from)] = 1
    choice_table = math.zeros(states.length, choices.length)
    data.edges.forEach (edge) ->
        choice_table._data[states.indexOf(edge.to)][choices.indexOf(edge.choice_id)] = edge.math
    return {
        "choice_table":choice_table
        "switch_table":switch_table
        "choices":choices
        "states":states
    }

window.gui_actions.loadMatricies = () ->
    return false
    
window.gui_actions.simulate = () ->
    matrix_info = gui_actions.getMatricies()
    config = {
        "simulate_params":{
            "target_trait_change":0.0000001,
            "repeated":15
        },
        "initial_reduction":0.4,
        "reduction_compaction":0.4,
        "MutateSimulation": {
            "simulate_params":{
                "target_quality": 0.000003
            },
            "mutation_shift": 0.4,
            "incorporation_factor": 0.3,
            "mutation_incorporation_factor": 0.8,
            "SubPopulationGrowthSimulation": {
                "smoothing_factor": 0.3
            }
        }
    }
    logs = {}
    console.log("SimulationStarting")
    console.log("switch_table - #{matrix_info['switch_table']}")
    console.log("choice_table - #{matrix_info['choice_table']}")
    simulation = new sim.EvolveSimulation(matrix_info['switch_table'], matrix_info['choice_table'], config, logs)
    simulation.simulate(0.01, 0.01)
    console.log("Simulationfinished")
    console.log("Final Genetics - #{simulation.getGenetics()}")
    console.log("Final Population - #{simulation.getPopulation()}")
    console.log("Final Growth_Rate - #{simulation.getGrowthRate()}")
    console.log("Final weighted_switch_table - #{simulation.getWeightedChoiceTable().toString()}")
    console.log("Final weighted_switch_table - #{simulation.getWeightedSwitchTable().toString()}")
    weighted_switch = simulation.getWeightedSwitchTable().toArray()
    for p,i in simulation.getPopulation().toArray()
        utils.modifyAllNodesWhere({id:matrix_info.states[i]}, {size:40*p[0], shape:"dot"})
        for c,o in matrix_info.choices
            utils.modifyAllEdgesWhere({from:matrix_info.states[i], choice_id:c}, {width:15*p[0]*weighted_switch[o][i]})
    $("#log-view").JSONView(logs)
        
    
    
    
    
    
    
    
