window.utils = {}

window.utils.isSubsetList = (A,B) ->
    return (a for a in A when a not in B).length == 0
window.utils.isSubsetObject = (A,B) ->
    return false not in (A[a]==B[a] for a in Object.keys(A))
window.utils.extendObject = (A,B) ->
    (A[b] = B[b] for b in Object.keys(B))
    return A

window.utils.getNodesWhere = (datum) ->
    ret = []
    data.nodes.forEach (node) ->
        if utils.isSubsetObject(datum, node)
            ret.push(node)
    return ret

window.utils.getEdgesWhere = (datum) ->
    ret = []
    data.edges.forEach (edge) ->
        if utils.isSubsetObject(datum, edge)
            ret.push(edge)
    return ret

window.utils.deleteAllEdgesWhere = (datum) ->
    to_remove = []
    data.edges.forEach (edge) ->
        if utils.isSubsetObject(datum, edge)
            to_remove.push(edge)
    for edge in to_remove
        data.edges.remove(edge)
            
window.utils.deleteAllNodesWhere = (datum) ->
    to_remove = []
    data.nodes.forEach (node) ->
        if utils.isSubsetObject(datum, node)
            to_remove.push(node)
    for edge in to_remove
        data.nodes.remove(edge)

window.utils.modifyAllNodesWhere = (bound, new_info) ->
    data.nodes.forEach (node) ->
        if utils.isSubsetObject(bound, node)
            utils.extendObject(node, new_info)
            data.nodes.update(node)

window.utils.modifyAllEdgesWhere = (bound, new_info) ->
    data.edges.forEach (edge) ->
        if utils.isSubsetObject(bound, edge)
            utils.extendObject(edge, new_info)
            old_id = edge.id
            edge.id = "#{edge.from}->#{edge.to}_w_#{edge.choice_id}"
            try
                data.edges.update(edge)
            catch error
                console.log("error detected when updating node #{old_id} to #{edge.id}; #{error} therefore removing")
                data.edges.remove(id:old_id)

window.utils.makeNewEdgesFor = (bound, new_info) ->
    to_add = []
    data.edges.forEach (edge) ->
        if utils.isSubsetObject(bound, edge)
            utils.extendObject(edge, new_info)
            try
                edge.id = "#{edge.from}->#{edge.to}_w_#{edge.choice_id}"
                to_add.push(edge)
    for e in to_add
        data.edges.add(e)

window.utils.forceNewEdgesFor = (bound, new_info) ->
    to_add = []
    data.edges.forEach (edge) ->
        if utils.isSubsetObject(bound, edge)
            utils.extendObject(edge, new_info)
            try
                edge.id = "#{edge.from}->#{edge.to}_w_#{edge.choice_id}"
                to_add.push(edge)
    for e in to_add
        try
            data.edges.add(e)
        catch
            data.edges.update(e)
