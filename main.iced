
$("#edgeMath").click (event) ->
    gui_actions.refreshField("math")
$("#edgeName").click (event) ->
    gui_actions.refreshField("name")
$("#edgeNone").click (event) ->
    gui_actions.refreshField("none")
$("#newchoicebutton").click (event) ->
    gui_actions.addChoice()
$("#selectionmathtype").on("change", () -> gui_actions.refresh())


container = document.getElementById 'graph' 
nodes = new vis.DataSet
edges = new vis.DataSet
window.data =
    nodes: nodes
    edges: edges

options =
    manipulation:
        initiallyActive: true
        addNode: gui_actions.addNode
        editNode: gui_actions.editNode
        deleteNode: gui_actions.deleteNode
        addEdge: gui_actions.addEdge
        deleteEdge: gui_actions.deleteEdge
    configure: true

window.network = new vis.Network(container, data, options)

#network.on("selectNode", function (params) {
#    console.log('selectNode Event:', params);
#});
network.on(
    "selectEdge"
    (params) ->
        if params.edges.length == 1
            gui_actions.refreshSelection(data.edges.get(params.edges[0]).choice_id)
        else
            console.log('Bad selectEdge Event:', params)
)

$("#newchoicebutton").click()

$("#Simulate").click (event) ->
    gui_actions.simulate()

children = $(".vis-configuration-wrapper").children()
for child, i in children
    if (i < 102) or (i > 114)
        $(child).hide()

config_template = {
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

window.config_tree = $("#sim-config").makeObjEditor(config_template, {"modifiable_form":false, "include_spacers":true})
