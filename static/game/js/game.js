function drawGame() {
    createMap()
    loadSettlements()
    loadUnits()
}

function createMap() {
    var layer = new Kinetic.Layer();

    for (var i = 0; i < MAP_WIDTH; i++) {
        for(var j = 0; j < MAP_HEIGHT; j++) {
            var field = new Kinetic.Rect({
                x: i * FIELD_SIZE,
                y: j * FIELD_SIZE,
                width: FIELD_SIZE,
                height: FIELD_SIZE,
                stroke: 'black'
            });
            layer.add(field);
        }
    }

    stage.add(layer);
}

$("#finish_stroke").click(function(){
    $.ajax({
        url : 'move_unit',
        data : {'pk':  this.pk, 'left': this.left, 'top': this.top},
        success : function(records) {
            var field = records[0].fields
            that.left = field.left;
            that.top = field.top;
            that.show()
        }
    });
});

drawGame();