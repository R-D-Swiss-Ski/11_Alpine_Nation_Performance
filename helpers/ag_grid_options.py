
grid_options_2 = {
    "columnDefs": [
        {
            "field": "Nation",
            "rowGroup": True,
            "enableRowGroup": True,
            "hide": True,
        },
        {   
            "field": "Discipline",
            "rowGroup": True,
            "hide": True,

        },
        {
            "field": "Wins",
            "aggFunc": "sum"
        },
            {
            "field": "2nd",
            "aggFunc": "sum"
        },
            {
            "field": "3rd",
            "aggFunc": "sum"
        },
            {
            "field": "[4-15]",
            "aggFunc": "sum"
        },
            {
            "field": "[16-30]",
            "aggFunc": "sum"
        },
            {
            "field": "WCPoints",
            "aggFunc": "sum"
        }
    ],
    "defaultColDef": {
    "flex": 1,
    "minWidth": 100,
    "resizable": True,
    "sortable": False,
    "autoHeaderHeight": True,
    "headerComponentParams": {
        "template":
        '<div class="ag-cell-label-container" role="presentation">' +
        '  <span ref="eMenu" class="ag-header-icon ag-header-cell-menu-button"></span>' +
        '  <div ref="eLabel" class="ag-header-cell-label" role="presentation">' +
        '    <span ref="eSortOrder" class="ag-header-icon ag-sort-order"></span>' +
        '    <span ref="eSortAsc" class="ag-header-icon ag-sort-ascending-icon"></span>' +
        '    <span ref="eSortDesc" class="ag-header-icon ag-sort-descending-icon"></span>' +
        '    <span ref="eSortNone" class="ag-header-icon ag-sort-none-icon"></span>' +
        '    <span ref="eText" class="ag-header-cell-text" role="columnheader" style="white-space: normal;text-align: right;"></span>' +
        '    <span ref="eFilter" class="ag-header-icon ag-filter-icon"></span>' +
        '  </div>' +
        '</div>'

    }

    },
    "autoGroupColumnDef": {
        "minWidth": 100,
        "headerName": "Nation",
        "pinned": "left",
        "sortable": True,
        "suppressMovable": True,
        "cellRendererParams":{
            "suppressCount": True,
        },

    },

    "suppressAggFuncInHeader": True,
    "removePivotHeaderRowWhenSingleValueColumn": True,

}