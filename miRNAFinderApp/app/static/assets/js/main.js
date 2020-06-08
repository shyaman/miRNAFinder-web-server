$('#predict').click(async function (e) {
    e.preventDefault();
    var seqfa = ''
    const ffile = $('#fafile').prop('files')[0];
    if(ffile){
        const reader = new FileReader();
        reader.readAsText(ffile);
        seqfa = await new Promise((resolve, reject) => {
            reader.onload = function(event) {
                resolve(reader.result)
            }
        })
    }
    
    
    seqfa = seqfa || $('#sequence').val()

    if(!seqfa) {
        alert("Input sequence")
    }else{
        $.ajax({
            url: '/validate',
            data: JSON.stringify({seq: seqfa}),
            type: 'POST',
            contentType: 'application/json',
            success: function(response) {
                if (response['valid']){
                    $('#submit-seq').hide();
                    $('#calculating').show();
                    $("#seq-form").submit();
                }else{
                    alert('Input valid sequence')
                }
            }
        });    
    }

});

$('#results').click(function(){
    $(this).text(function(i,old){
        return old=='Show Results' ?  'Hide Results' : 'Show Results';
    });
});