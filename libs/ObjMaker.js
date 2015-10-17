//Created: Mark A. Burgess - 5/10/2015

(function (document, $) {
    context = function(container, config) {
        var class_names, drop_labels, include_spacers, refreshHandler, modifiable_form
        
        // set configuration variables to config dictionary/object
        function resetConfig(config) {
            if (!config) {
                config = {}
            }
            class_names = config['class_names']
            if (class_names == undefined) {
                class_names = {string_content:"string_content",
                               numeric_content:"numeric_content",
                               array_content:"array_content",
                               object_content:"object_content",
                               sub_element:"sub_element",
                               content:"content",
                               container:"container",
                               spacer:"spacer",
                               additional:"additional",
                               needed:"needed",
                               duplicate:"duplicate",
                               name_box:"name_box"}
            }
            drop_labels = config['drop_labels']
            if (drop_labels == undefined) {
                drop_labels = {None:"",
                               String:"String",
                               Number:"Number",
                               Array:"Array",
                               Object:"Object"}
            }
            include_spacers = config['include_spacers']
            refreshHandler = config['refreshHandler']
            modifiable_form = config['modifiable_form']
            if (modifiable_form == undefined) {
                modifiable_form = true
            }
        }
        //call it
        resetConfig(config)
        
        // manually set the refresh handler hook
        function setRefreshHandler(handler) {
            refreshHandler = handler
        }
        // Given the 'content' DOM object of a presumed string field, return the string otherwise empty string 
        function getString(element) {
            element = $(element)
            if (element && element.attr("class") && element.attr("class").indexOf(class_names["string_content"]) > -1) {
                return element.children("input").val()
            } else {
                return ""
            }
        }
        // Given the 'content' DOM object of a presumed numeric field, return the string otherwise zero 
        function getNumeric(element) {
            element = $(element)
            if (element && element.attr("class") && element.attr("class").indexOf(class_names["numeric_content"]) > -1) {
                return parseFloat(element.children("input[type=number]").val())
            } else {
                return 0
            }
        }
        // Given the 'content' DOM object of a presumed Array field/s, return the array otherwise empty-array 
        function getArray(element) {
            element = $(element)
            if (element && element.attr("class") && element.attr("class").indexOf(class_names["array_content"]) > -1) {
                var obj_elements = element.children("."+class_names["sub_element"])
                var array = []
                for (var i = 0; i < obj_elements.length; i++) {
                    var obj_children = $(obj_elements[i]).children()
                    var type = obj_children.filter("select").val()
                    if (type != drop_labels["None"]) {
                        var content = obj_children.filter("."+class_names['content'])
                        if (type == drop_labels["String"]) {
                            array.push(getString(content))
                        } else if (type == drop_labels["Number"]) {
                            array.push(getNumeric(content))
                        } else if (type == drop_labels["Array"]) {
                            array.push(getArray(content))
                        } else if (type == drop_labels["Object"]) {
                            array.push(getObject(content))
                        } else {
                            throw "wtf"
                        }
                    }
                }
                return array
            } else {
                return []
            }
        }
        // Given the 'content' DOM object of a presumed Object field, return the processed object otherwise empty-object, NOTE: throws 'duplicate_presnt' if there exists a duplicate name in the inputs 
        function getObject(element) {
            element = $(element)
            if (element && element.attr("class") && element.attr("class").indexOf(class_names["object_content"]) > -1) {
                var obj_elements = element.children("."+class_names['sub_element'])
                var obj = {}
                for (var i = 0; i < obj_elements.length; i++) {
                    var obj_children = $(obj_elements[i]).children()
                    var type = obj_children.filter("select").val()
                    if (type != drop_labels["None"]) {
                        var label = obj_children.filter("input").val()
                        if (label == undefined) {
                            label = ""
                        }
                        var content = obj_children.filter("."+class_names['content'])
                        if (obj[label] != undefined) {
                            obj_children.filter("input").addClass(class_names["duplicate"])
                            throw "duplicate_present"
                        }
                        if (type == drop_labels["String"]) {
                            obj[label] = getString(content)
                        } else if (type == drop_labels["Number"]) {
                            obj[label] = getNumeric(content)
                        } else if (type == drop_labels["Array"]) {
                            obj[label] = getArray(content)
                        } else if (type == drop_labels["Object"]) {
                            obj[label] = getObject(content)
                        } else {
                            throw "wtf"
                        }
                    }
                }
                return obj
            } else {
                return {}
            }
        }
        //for a given DOM element, make a selection box of possible types
        function makeTypeSelect(element) {
            element = $(element)
            var sel = $("<select></select")
            $("<option>"+drop_labels["None"]+"</option>").appendTo(sel)
            $("<option>"+drop_labels["String"]+"</option>").appendTo(sel)
            $("<option>"+drop_labels["Number"]+"</option>").appendTo(sel)
            $("<option>"+drop_labels["Array"]+"</option>").appendTo(sel)
            $("<option>"+drop_labels["Object"]+"</option>").appendTo(sel)
            sel.appendTo(element)
            return sel
        }
        //for a give 'string_content' DOM div, populate with string field
        function makeString(element, entity) {
            element = $(element)
            var input = $("<input></input>")
            input.val(entity).change(refresh)
            input.appendTo(element)
        }
        //for a give 'numeric_content' DOM div, populate with numeric field
        function makeNumeric(element, entity) {
            element = $(element)
            var input = $("<input type=number></input>")
            input.val(entity).change(refresh)
            input.appendTo(element)
        }
        //for a give 'array_content' DOM div, populate with all fields from the array
        function makeArray(element, entity) {
            element = $(element)
            for (var i = 0; i < entity.length; i++) {
                var value = entity[i]
                if (include_spacers) {
                    $('<div class="'+class_names["spacer"]+'"></div>').appendTo(element)
                }
                var sub_element = $('<div class="'+class_names["sub_element"]+'"></div>')
                sub_element.appendTo(element)
                var type_select = makeTypeSelect(sub_element)
                if (modifiable_form) {
                    type_select.change(refresh)
                } else {
                    type_select.prop("disabled", true)
                }
                type_select.val(makeEntity(sub_element, value))
            }
            if (modifiable_form) {
                if (include_spacers) {
                    $('<div class="'+class_names["spacer"]+'"></div>').appendTo(element)
                }
                var new_sub_element = $("<div class='"+class_names["sub_element"]+"'></div>")
                new_sub_element.appendTo(element)
                makeTypeSelect(new_sub_element).addClass(class_names["additional"]).change(refresh)
            }
        }
        //for a give 'object_content' DOM div, populate with all fields from the object
        function makeObject(element, entity) {
            element = $(element)
            var keys = Object.keys(entity)
            var has_undefined_key = false
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i]
                var value = entity[key]
                if (include_spacers) {
                    $('<div class="'+class_names["spacer"]+'"></div>').appendTo(element)
                }
                var sub_element = $('<div class="'+class_names["sub_element"]+'"></div>')
                sub_element.appendTo(element)
                var type_select = makeTypeSelect(sub_element)
                var name_box = $("<input class='"+class_names["name_box"]+"'></input>")
                name_box.val(key)
                name_box.appendTo(sub_element)
                if (modifiable_form) {
                    type_select.change(refresh)
                    name_box.data("prev", key)
                    name_box.change(revert_refresh)
                } else {
                    type_select.prop("disabled", true)
                    name_box.prop("disabled", true)
                }
                if (key == "") {
                    has_undefined_key = true
                    name_box.addClass(class_names["needed"])
                }
                type_select.val(makeEntity(sub_element, value))
            }
            if ((!has_undefined_key) && (modifiable_form)) {
                if (include_spacers) {
                    $('<div class="'+class_names["spacer"]+'"></div>').appendTo(element)
                }
                var new_sub_element = $("<div class='"+class_names["sub_element"]+"'></div>")
                new_sub_element.appendTo(element)
                makeTypeSelect(new_sub_element).addClass(class_names["additional"]).change(refresh)
            }
        }
        //for a given DOM element, and an arbitary -simple- entity, make appropriate 'content' div, and populate
        function makeEntity(element, entity) {
            element = $(element)
            var new_content
            if (typeof entity == "string") {
                new_content = $("<div class='"+class_names['string_content']+" "+class_names["content"]+"'></div>")
                new_content.appendTo(element)
                makeString(new_content, entity)
                return drop_labels["String"]
            } else if ($.isNumeric(entity)) {
                new_content = $("<div class='"+class_names['numeric_content']+" "+class_names["content"]+"'></div>")
                new_content.appendTo(element)
                makeNumeric(new_content, entity)
                return drop_labels["Number"]
            } else if ($.isArray(entity)) {
                new_content = $("<div class='"+class_names['array_content']+" "+class_names["content"]+"'></div>")
                new_content.appendTo(element)
                makeArray(new_content, entity)
                return drop_labels["Array"]
            } else if ($.isPlainObject(entity)) {
                new_content = $("<div class='"+class_names['object_content']+" "+class_names["content"]+"'></div>")
                new_content.appendTo(element)
                makeObject(new_content, entity)
                return drop_labels["Object"]
            } else {
                throw "oops cannot parse-in " + entity
            }
        }
        // try to refresh, and if duplicte-name-error is thrown then alert and revert the change
        function revert_refresh() {
            try {
                refresh()
            } catch(e) {
                if (e == "duplicate_present") {
                    alert("cannot create object with duplicate named entries")
                    $(this).val($(this).data("prev"))
                    revert_refresh()
                } else {
                    throw e
                }
            }
        }
        //refresh everything about the graph and call refresh_handler
        function refresh() {
            var obj = getObject(container.children("."+class_names["content"]))
            container.empty()
            makeEditor(obj)
            if (refreshHandler) {
                refreshHandler(obj)
            }
        }
        //under the assumption that the initial container is empty, set the class of the container appropriate and create the DOM graph from argument.
        function makeEditor(initial) {
            if (initial == undefined) {
                initial = {}
            }
            element = $(container).addClass(class_names["container"])
            makeEntity(container, initial)
        }
        //set the DOM graph to given object, and call refresh_handler
        function set(obj) {
            container.empty()
            makeEditor(obj)
            if (refreshHandler) {
                refreshHandler(obj)
            }
        }
        //get the javascript-object from the DOM fields
        function get() {
            return getObject(container.children("."+class_names["content"]))
        }
        //return control
        return {
            "set": set,
            "get": get,
            "setRefreshHandler": setRefreshHandler,
            "resetConfig": resetConfig
        }
    }
    
    $.makeObjEditor = function(element, initial, config) {
        var ctx = context(element, config)
        ctx.set(initial)
        return ctx
    }
    $.fn.makeObjEditor = function(initial, config) {
        var ctx = context(this, config)
        ctx.set(initial)
        return ctx
    }
})(document, jQuery);
