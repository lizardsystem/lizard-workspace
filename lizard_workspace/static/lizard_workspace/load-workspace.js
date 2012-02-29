
({
  itemId: 'maatregelen-beheer',
  title: 'maatregelen-beheer',
  xtype: 'portalpanel',
  items: [
    {
      flex: 1,
      items: [
        {
          title: 'Maatregelen',
          anchor: '100%',
          flex: 1,
          xtype: 'leditgrid',
          columnLines: true,
          plugins: ['applycontext'],
          applyParams: function(params) {
            params = params || {};
            console.log('apply params on store:');
            console.log(params);
            if (this.store) return this.store.load();
          },
          proxyUrl: '/measure/api/measure/',
          proxyParams: {
            flat: false,
            size: 'small',
            include_geom: false
          },
          addEditIcon: true,
          addDeleteIcon: false,
          actionEditIcon: function(record) {
            var me, params;
            me = this;
            console.log(this.store.getNewRecords());
            if (this.store.getNewRecords().length > 0 || this.store.getUpdatedRecords().length > 0 || this.store.getRemovedRecords().length > 0) {
              Ext.Msg.alert("Let op", 'Sla eerst de bewerking(en) in het grid op, voordat een enkel record kan worden bewerkt');
              return;
            }
            console.log('edit record:');
            console.log(record);
            if (record) {
              params = {
                measure_id: record.data.id
              };
            } else {
              params = null;
            }
            return Ext.create('Ext.window.Window', {
              title: 'Maatregel',
              width: 800,
              height: 600,
              modal: true,
              finish_edit_function: function(updated_record) {
                return me.store.load();
              },
              editpopup: true,
              loader: {
                loadMask: true,
                autoLoad: true,
                url: '/measure/measure_detailedit_portal/',
                ajaxOptions: {
                  method: 'GET'
                },
                params: params,
                renderer: 'component'
              }
            }).show();
          },
          addRecord: function() {
            return this.actionEditIcon();
          },
          dataConfig: [
            {
              name: 'id',
              title: 'id',
              editable: false,
              visible: false,
              width: 30,
              type: 'number'
            }, {
              name: 'ident',
              title: 'ident',
              editable: false,
              visible: false,
              width: 100,
              type: 'text'
            }, {
              name: 'title',
              title: 'titel',
              editable: true,
              visible: true,
              width: 200,
              type: 'text'
            }, {
              name: 'is_KRW_measure',
              title: 'KRW maatregel',
              editable: true,
              visible: true,
              width: 100,
              type: 'boolean'
            }, {
              name: 'is_indicator',
              title: 'focus maatregel',
              editable: true,
              visible: true,
              width: 100,
              type: 'boolean'
            }, {
              name: 'parent',
              title: 'onderdeel van',
              editable: false,
              visible: true,
              width: 75,
              type: 'combo'
            }, {
              name: 'value',
              title: 'waarde',
              editable: true,
              visible: true,
              width: 75,
              type: 'number'
            }, {
              name: 'initiator',
              title: 'initiatiefnemer',
              editable: true,
              visible: true,
              width: 100,
              type: 'combo',
              remote: true,
              store: {
                fields: ['id', 'name'],
                proxy: {
                  type: 'ajax',
                  url: '/measure/api/organization/?_accept=application%2Fjson&size=id_name',
                  reader: {
                    type: 'json',
                    root: 'data'
                  }
                }
              }
            }, {
              name: 'executive',
              title: 'uitvoerder',
              editable: true,
              visible: true,
              width: 100,
              type: 'combo',
              remote: true,
              store: {
                fields: ['id', 'name'],
                proxy: {
                  type: 'ajax',
                  url: '/measure/api/organization/?_accept=application%2Fjson&size=id_name',
                  reader: {
                    type: 'json',
                    root: 'data'
                  }
                }
              }
            }, {
              name: 'responsible_department',
              title: 'afdeling',
              editable: true,
              visible: true,
              width: 75,
              type: 'text'
            }, {
              name: 'total_costs',
              title: 'totale kosten',
              editable: false,
              visible: true,
              width: 75,
              type: 'number'
            }, {
              name: 'investment_costs',
              title: 'investeringskosten',
              editable: true,
              visible: true,
              width: 75,
              type: 'number'
            }, {
              name: 'exploitation_costs',
              title: 'exploitatiekosten',
              editable: true,
              visible: true,
              width: 75,
              type: 'number'
            }, {
              name: 'waterbodies',
              title: 'KRW waterlichamen',
              editable: false,
              visible: true,
              width: 100,
              type: 'gridcombobox'
            }, {
              name: 'areas',
              title: 'Aan/ afvoergebieden',
              editable: false,
              visible: true,
              width: 100,
              type: 'gridcombobox'
            }
          ]
        }
      ]
    }
  ]
})
