odoo.define('uc_construction.header', function (require) {
    "use strict";

    const SectionAndNoteListRenderer = require('account.section_and_note_backend');
    var ListRenderer = require('web.ListRenderer');
    var super_section = ListRenderer.prototype;
    SectionAndNoteListRenderer.include({

        _renderBodyCell: function (record, node, index, options) {
            var $cell = super_section._renderBodyCell.apply(this, arguments);
            var isSection = record.data.display_type === 'line_section';
            var isNote = record.data.display_type === 'line_note';
            if (record.model!='uc.tender.item'){
                  if (isSection || isNote) {
                if (node.attrs.widget === "handle") {
                    return $cell;
                } else if (node.attrs.name === "name") {
                    var nbrColumns = this._getNumberOfCols();
                    if (this.handleField) {
                        nbrColumns--;
                    }
                    if (this.addTrashIcon) {
                        nbrColumns--;
                    }
                    $cell.attr('colspan', nbrColumns);
                } else {
                    $cell.removeClass('o_invisible_modifier');
                    return $cell.addClass('o_hidden');
                }
            }
            }



            return $cell;
        },
        /**
         * We add the o_is_{display_type} class to allow custom behaviour both in JS and CSS.
         *
         * @override
         */
        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);

            if (record.data.display_type) {
                $row.addClass('o_is_' + record.data.display_type);
            }

            return $row;
        },


    });


});