function drawGame() {
    createMap()
    loadSettlements()
    loadUnits()
    loadPlayer()
}

function clearGame() {
    hidePurchasesPanel()
    delete Unit
    delete Settlement
    delete Player
    stage.clear()
}

function createMap() {
    var layer = new Kinetic.Layer();
    var image = new Image()
    var map = new Kinetic.Image({
        x: 0,
        y: 0,
        image: image,
        width: 1300,
        height: 600,
        listening: false
    });
    image.onload = function() {
        layer.add(map)
        layer.moveToBottom()
        layer.draw()
    };
    image.src = "/static/game/img/map.jpg"
    stage.add(layer);
}

$("#finishStroke").click(function(){
    $.ajax({
        url : 'finish_stroke',
        data : {'player':  1},
        success : function() {
            clearGame();
            drawGame();
        }
    });
});

drawGame();

