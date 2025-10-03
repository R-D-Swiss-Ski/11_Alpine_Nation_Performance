
from st_aggrid import JsCode


custom_css={
    "#gridToolBar": {
        "padding-bottom": "0px !important",
    },
    ".ag-header-cell": {
        "background-color": "white !important",
        "border-bottom": "1px solid grey !important",
        "font-weight": "bold !important",
        "color": "black !important",
    },
    ".ag-row:nth-child(even)": {
        "background-color": "#f2f2f2 !important",  # Light grey color for even rows
    },
    ".ag-row:nth-child(odd)": {
        "background-color": "white !important",  # White color for odd rows
}   

}




grid_options = {
    "columnDefs": [
        {
            "field": "Nation",
            "rowGroup": True,
            "hide": True,
            "suppressMovable": True,
        },
        {   
            "field": "Discipline",
            "rowGroup": True,

        },
        {
            'field': 'Gender',
            'rowGroup': True
        },
        {
            "field": "column_name",
            "pivot": True,
            "pivotComparator": JsCode("""function(a, b) {
                const order = {
                    'Wins': 1,
                    '2nd': 2,
                    '3rd': 3,
                    '[4-15]': 4,
                    '[16-30]': 5,
                    'WCPoints': 6
                };
                const orderA = order[a] || 999;
                const orderB = order[b] || 999;
                return orderA - orderB;
            }""")
        },
            {
            "field": "value",
            "aggFunc": "sum",
            "sortable": True,
        },
         
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
    "pagination": True,
    "pivotMode": True

}

grid_options_1 = {
    "columnDefs": [
        {
            "field": "Nation",
            "rowGroup": True,
            "hide": True,
            "suppressMovable": True,
        },
        {   
            "field": "Discipline",
            "rowGroup": True,

        },
        {
            "field": "column_name",
            "pivot": True,
        },
            {
            "field": "value",
            "aggFunc": "avg",
            "sortable": True,
            "type": ['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
            "precision": 1,
            "valueGetter": JsCode("""
                function(params) {
                    // If this is a group row, return null (hide aggregated value)
                    if (params.node.group) {
                        return null;
                    }
                    // Otherwise, show actual value
                    return params.data ? params.data.value : null;
                }
            """),
        },
         
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
    "pagination": True,
    "pivotMode": True

}
