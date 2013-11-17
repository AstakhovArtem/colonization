function Unit(player, type, position) {
    this.player = player
    this.type = type
    this.position = position
}

Unit.prototype.show = function() {
    var layer = new Kinetic.Layer();
    var x = (this.position[0] - 1) * FIELD_SIZE
    var y = (this.position[1] - 1) * FIELD_SIZE

    var border = new Kinetic.Rect({
        x: x - FIELD_SIZE,
        y: y - FIELD_SIZE,
        width: 3 * FIELD_SIZE,
        height: 3 * FIELD_SIZE,
        stroke: 'red',
        strokeWidth: 2.5,
        listening: false
    });

    var unit = new Kinetic.Rect({
        x: x,
        y: y,
        width: FIELD_SIZE,
        height: FIELD_SIZE,
        fill: 'red',
        draggable: true,
        dragBoundFunc: function(pos) {
            var newY = pos.y;
            if(pos.y < y - FIELD_SIZE) newY = y - FIELD_SIZE;
            else if(pos.y > y + FIELD_SIZE) newY = y + FIELD_SIZE;
            var newX = pos.x;
            if(pos.x < x - FIELD_SIZE) newX = x - FIELD_SIZE;
            else if(pos.x > x + FIELD_SIZE) newX = x + FIELD_SIZE;

            return {
                x: newX,
                y: newY
            };
        }
    });

    unit.on('mouseup', function() {
        layer.destroyChildren()
        layer.destroy()
        var absolutePosition = stage.getPointerPosition()
        var position = [parseInt(absolutePosition.x / FIELD_SIZE) + 1, parseInt(absolutePosition.y / FIELD_SIZE) + 1]
        new Unit(this.player, this.type, position).show()
        delete this
    });

    unit.on('mousedown', function() {
        if (layer.children.length == 2) layer.add(border)
    });

    var shadow = new Kinetic.Rect({
        x: x,
        y: y,
        width: FIELD_SIZE,
        height: FIELD_SIZE,
        fill: 'red',
        opacity: 0.5
    });

    layer.add(shadow);
    layer.add(unit);
    stage.add(layer);
}