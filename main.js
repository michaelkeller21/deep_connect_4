//main listener, allows all immediate functionality to occur


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

            game_state: "",
        }
    })

/*
function move(index) {
    console.log(app.full[0]);
    const col = app.grid[index].reverse();
    for(const idx in col){
        const val = col[idx];
        if(!val) {
            if(idx == col.length - 1) {
                app.full.splice(index, 1, 1);
            }
                app.grid[index].splice(idx, 1, 1);
                app.grid[index].reverse();
                break;
        }
    }
    ai_move();
}
*/
function move(index) {
    idx = search_available_pos(index);

    app.grid[index].splice(app.grid[index].length - idx - 1, 1, 1);
    update_game_state();
    ai_move();
    update_game_state();

}

function ai_move() {
    var idx = Math.floor(Math.random() * 7);
    while(app.full[idx] == 1) {
        idx = Math.floor(Math.random() * 7);
    }
    app.grid[idx].splice(app.grid[idx].length - search_available_pos(idx) - 1, 1, 2)

}

function search_available_pos(index) {
    const col = app.grid[index].reverse();
    for (const idx in col) {
        const val = col[idx];
        if (!val) {
            app.grid[index].reverse();
            return idx;
        }
    }
    app.grid[index].reverse();
    console.log("all the way here");
    return -1;
}

function update_game_state(){
    var count = 0;
    for(const index in app.full) {
        console.log(index);
        const idx = search_available_pos(index);

        if (idx == -1) {
            app.full.splice(index, 1, 1);
            count += 1;
        }
    }
}