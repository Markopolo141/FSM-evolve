window.questions = {}

window.questions.askEquation = (save_callback, cancel_callback, text) ->
    option_box = $("#OptionBox")
        .empty()
    option_box.mk(""
        text
        $.mk("br")
        $.mk("br")
        dummyprint = $.mk("span[style=display:none;]")
        realprint = $.mk("span")
        $.mk("br")
        $.mk("br")
        input = $.mk("input[style=width:100%;]")
        save = $.mk("input[type=button][value=save]")
        cancel = $.mk("input[type=button][value=cancel]")
    )
    equation_change = null
    refresh = () ->
        clearTimeout(equation_change)
        equation_change = setTimeout(
            ((text)->()-> 
                dummyprint.text(text)
                MathJax.Hub.Queue(["Typeset",MathJax.Hub,dummyprint[0]])
                MathJax.Hub.queue.Push( ()->
                    realprint.html(dummyprint.html())
                )
            )("`#{input.val()}`")
            500
        )
    cancel.click () ->
        cancel_callback()
        option_box.hide()
    save.click () ->
        if save_callback(input.val()) != false
            option_box.hide()
    input.on("propertychange change input", refresh)
    input.keydown (event) -> 
        if event.keyCode == 13
            save.click()
    option_box.show()
    refresh()
    input.focus()

window.questions.askString = (save_callback, cancel_callback, text) ->
    option_box = $("#OptionBox")
        .empty()
    option_box.mk(""
        text
        $.mk("br")
        $.mk("br")
        input = $.mk("input[style=width:100%]")
        save = $.mk("input[type=button][value=save]")
        cancel = $.mk("input[type=button][value=cancel]")
    )
    cancel.click () ->
        cancel_callback()
        option_box.hide()
    save.click () -> 
        if save_callback(input.val()) != false
            option_box.hide()
    input.keydown (event) -> 
        if event.keyCode == 13
            save.click()
    option_box.show()
    input.focus()

window.questions.askConfirm = (yes_callback, no_callback, text) ->
    option_box = $("#OptionBox")
        .empty()
    option_box.mk(""
        text
        $.mk("br")
        $.mk("br")
        yesbutton = $.mk("input[type=button][value=Yes]")
        nobutton = $.mk("input[type=button][value=No]")
    )
    nobutton.click () ->
        no_callback()
        option_box.hide()
    yesbutton.click () ->
        yes_callback()
        option_box.hide()
    option_box.show()
    yesbutton.focus()
    
window.questions.askTristate = (a_callback, b_callback, c_callback, text, a_text, b_text, c_text) ->
    option_box = $("#OptionBox")
        .empty()
    option_box.mk(""
        text
        $.mk("br")
        $.mk("br")
        abutton = $.mk("input[type=button][value=#{a_text}]")
        bbutton = $.mk("input[type=button][value=#{b_text}]")
        cbutton = $.mk("input[type=button][value=#{c_text}]")
    )
    abutton.click () ->
        a_callback()
        option_box.hide()
    bbutton.click () ->
        b_callback()
        option_box.hide()
    cbutton.click () ->
        c_callback()
        option_box.hide()
    option_box.show()
    abutton.focus()

window.questions.notifyConfirm = (callback, text) ->
    option_box = $("#OptionBox")
        .empty()
    option_box.mk(""
        text
        $.mk("br")
        $.mk("br")
        okbutton = $.mk("input[type=button][value=Ok]")
    )
    okbutton.click () ->
        callback()
        option_box.hide()
    option_box.show()
    okbutton.focus()
    
