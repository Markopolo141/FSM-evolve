window.actions = {}

window.actions.addEdge = (choiceData, edgeData) ->
    edge_base = utils.extendObject(
        arrows: to: scaleFactor: 0.7
        font: align: 'middle',
        choiceData
    )
    utils.forceNewEdgesFor(
        choice_id: choiceData.choice_id
        utils.extendObject(to:edgeData.to, math: edgeData.math, edge_base)
    )
    utils.forceNewEdgesFor(
        choice_id: choiceData.choice_id
        utils.extendObject(from:edgeData.from, edge_base)
    )
    edgeData.id = "#{edgeData.from}->#{edgeData.to}_w_#{choiceData.choice_id}"
    try
        data.edges.add(utils.extendObject(edgeData, edge_base))
        return true
    catch
        return false

window.actions.removeEdgesFrom = (edgeData) ->
    utils.deleteAllEdgesWhere(
        choice_id: edgeData.choice_id
        from: edgeData.from
    )
    return true

window.actions.removeEdgesTo = (edgeData) ->
    utils.deleteAllEdgesWhere(
        choice_id: edgeData.choice_id
        to: edgeData.to
    )
    return true

window.actions.addNode = (nodeData) ->
    if utils.getNodesWhere(label:nodeData.label).length != 0
        return false
    try
        data.nodes.add(nodeData)
    catch
        return false

window.actions.removeNode = (nodeData) ->
    data.nodes.remove(nodeData)
    return true
    
window.actions.addChoice = (choiceData) ->
    return true

window.actions.removeChoice = (choiceData) ->
    utils.deleteAllEdgesWhere(
        choice_id: choiceData.choice_id
    )
    return true

window.actions.alterChoice = (choiceData, new_data) ->
    utils.modifyAllEdgesWhere(choiceData, new_data)
    return true














