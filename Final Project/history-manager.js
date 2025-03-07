// history-manager.js
export class HistoryManager {
    constructor() {
        this.history = {};
    }

    addItem(type, input, data) {
        console.log(`Adding ${type} to history:`, { input, data });
        if (!this.history[type]) this.history[type] = [];
        const item = { id: Date.now(), input, data };
        this.history[type].unshift(item);
        if (this.history[type].length > 10) this.history[type].pop();
    }

    getLastItem(type) {
        return this.history[type]?.[0];
    }
}