var model;
tf.loadLayersModel('models/1/model.json').then((models) => {
    model = models
    console.log('loaded model')
});

var app = new Vue({
        el: '#app',
        data: {
            grid: [[0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   ],
            pred: [0, 0, 0, 0, 0, 0, 0],
            full: [0, 0, 0, 0, 0, 0, 0],
            status: "in progress",
            players: [-1, 1],
            h: 6,
            w: 7,
            consecutive: 4,
            message: '',
        }
    })

function move(index) {
    if(!app.full[index]) {
        idx = fill_col(index);

        app.grid[index].splice(app.grid[index].length - idx - 1, 1, 1);
        update_state();
    }

    if(app.status != 'end') {
        ai_move();
        update_state();
    }

}

function ai_move() {
    /*
    var idx = Math.floor(Math.random() * 7);
    while(app.full[idx] == 1) {
        idx = Math.floor(Math.random() * 7);
    }*/

    const input = grid_to_tensor(app.grid);
    var pred = model.predict(input).dataSync();
    idx = pred.indexOf(Math.max.apply(false, pred));

    // if the model predicts a filled index we find the next available index
    while(app.full[idx]){
        pred[idx] = 0;
        idx = pred.indexOf(Math.max.apply(false, pred))
    }

    /*
    pred_round = pred.map(function(each_element){
    return Number(each_element.toFixed(1));
    });*/
    pred_arr = Array.from(pred);
    const pred_round = pred_arr.map(x => (Math.round(x * 100) / 100));

    Vue.set(app, 'pred', pred_round);
    app.grid[idx].splice(app.grid[idx].length - fill_col(idx) - 1, 1, -1)
}

function grid_to_tensor(){
    var output1 = [[0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   ];
    var output2 = JSON.parse(JSON.stringify(output1));
    const grid = app.grid;

    for(var i = 0; i <= app.h; i++){
        for(var j = 0; j <= app.w; j++){
            if(grid[i][j] == -1)
                output1[i][j] = 1;
            else if(grid[i][j] == 1){
                output2[i][j] = 1;
            }
        }
    }
    return tf.stack([tf.tensor2d(output1).toInt(), tf.tensor2d(output2).toInt()], 2).expandDims();

}

function fill_col(index) {
    const col = app.grid[index].reverse();
    for (const idx in col) {
        const val = col[idx];
        if (!val) {
            app.grid[index].reverse();
            return idx;
        }
    }
    app.grid[index].reverse();
    return -1;
}

function update_state(){
    for(const index in app.full) {
        const idx = fill_col(index);

        // checking for full columns
        if (idx == -1) {
            app.full.splice(index, 1, 1);
        }

        winner = check_win();

        if (winner){
            app.status = 'end';
            if(winner == app.players[1]){
                app.message = "You win!";
            }
            else{
                app.message = "AI wins!"
            }
        }
    }
}

function check_win() {
    for(var i = 0; i < app.players.length; i++) {
        player = app.players[i];
        const win_seq = (current) => current == player;

        grid_T = transpose(app.grid);
        grid = app.grid;

        // Testing vertical win
        for(var j = 0; j < app.w; j++) {
            col = grid[j];
            for(var k = 0; k <= app.h - app.consecutive; k++){
                const slice = col.slice(k, k + app.consecutive);
                if(slice.every(win_seq)){
                    console.log("verti", player);
                    return player;
                }
            }
        }

        // Testing horizontal win
        for(var j = 0; j < app.h; j++) {
            row = grid_T[j];
            for(var k = 0; k <= app.w - app.consecutive; k++){
                const slice = row.slice(k, k + app.consecutive);
                if(slice.every(win_seq)){
                    console.log("hori", player);
                    return player;
                }
            }
        }
        // Testing diagonal win
        grids = [grid, grid_T];

        for(grid_idx in grids) {
            curr_grid = grids[grid_idx];
            for (var j = 0; j <= app.h - app.consecutive; j++) {
                temp = [];
                for (var ll = 0; ll <= app.w - app.consecutive; ll++) {
                    for (var k = 0; k < app.consecutive; k++) {
                        if(grid_idx) {
                            temp[k] = curr_grid[j + k][ll + k];
                        } else {
                            temp[k] = curr_grid[ll + k][j + k];
                        }
                    }
                    for (var n = 0; n <= app.w - app.consecutive; n++) {
                        const slice = temp.slice(n, n + app.consecutive);

                        if (slice.every(win_seq) && slice.length == 4) {
                            console.log("diag", player);
                            return player;
                        }
                    }
                }
            }
        }
    }
    return false;
}

function transpose(m){
    return m[0].map((col, i) => m.map(row => row[i]));
}

function reset_board(){
    app.grid = [[0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                ];
    app.full = [0, 0, 0, 0, 0, 0, 0];
    app.pred = [0, 0, 0, 0, 0, 0, 0];
    app.status = 'in progress';
    app.message = '';
}
