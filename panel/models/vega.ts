import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {isArray} from "@bokehjs/core/util/types"
import {HTMLBox, HTMLBoxView} from "./layout"
import {Attrs} from "@bokehjs/core/types"

import {debounce} from  "debounce"

export class VegaEvent extends ModelEvent {
  event_name: string = "vega_event"

  constructor(readonly data: any) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }
}

export class VegaPlotView extends HTMLBoxView {
  model: VegaPlot
  vega_view: any
  _callbacks: string[]
  _connected: string[]

  connect_signals(): void {
    super.connect_signals()
    const {data, show_actions, theme} = this.model.properties
    this.on_change([data, show_actions, theme], () => {
      this._plot()
    })
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources())
    this.connect(this.model.properties.events.change, () => {
      for (const event of this.model.events) {
        if (this._callbacks.indexOf(event) > -1)
          continue
        this._callbacks.push(event)
        const callback = (name: string, value: any) => this._dispatch_event(name, value)
        const timeout = this.model.throttle[event] || 20
        this.vega_view.addSignalListener(event, debounce(callback, timeout, false))
      }
    })
    this._connected = []
    this._connect_sources()
  }

  _connect_sources(): void {
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds]
      if (this._connected.indexOf(ds) < 0) {
        this.connect(cds.properties.data.change, this._plot)
        this._connected.push(ds)
      }
    }
  }

  _dispatch_event(name: string, value: any): void {
    if ('vlPoint' in value && value.vlPoint.or != null) {
      const indexes = []
      for (const index of value.vlPoint.or)
        indexes.push(index._vgsid_)
      value = indexes
    }
    this.model.trigger_event(new VegaEvent({type: name, value: value}))
  }

  _fetch_datasets() {
    const datasets: any = {}
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds];
      const data: any = []
      const columns = cds.columns()
      for (let i = 0; i < cds.get_length(); i++) {
        const item: any = {}
        for (const column of columns) {
          item[column] = cds.data[column][i]
        }
        data.push(item)
      }
      datasets[ds] = data;
    }
    return datasets
  }

  render(): void {
    super.render()
    this.el = div()
    this._callbacks = []
    this._plot()
    this.shadow_el.append(this.el)
  }

  _plot(): void {
    const data = this.model.data
    if ((data == null) || !(window as any).vegaEmbed)
      return
    if (this.model.data_sources && (Object.keys(this.model.data_sources).length > 0)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        data.data['values'] = datasets['data']
        delete datasets['data']
      }
      if (data.data != null) {
        const data_objs = isArray(data.data) ? data.data : [data.data]
        for (const d of data_objs) {
          if (d.name in datasets) {
            d['values'] = datasets[d.name]
            delete datasets[d.name]
          }
        }
      }
      this.model.data['datasets'] = datasets
    }
    const config: any = {actions: this.model.show_actions, theme: this.model.theme};

    (window as any).vegaEmbed(this.el, this.model.data, config).then((result: any) => {
      this.vega_view = result.view
      if (this.vega_view._viewHeight <= 0 || this.vega_view._viewWidth <= 0) {
        (window as any).dispatchEvent(new Event('resize'));
      }
      const callback = (name: string, value: any) => this._dispatch_event(name, value)
      for (const event of this.model.events) {
        this._callbacks.push(event)
        const timeout = this.model.throttle[event] || 20
        this.vega_view.addSignalListener(event, debounce(callback, timeout, false))
      }
    })
  }
}

export namespace VegaPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    data_sources: p.Property<any>
    events: p.Property<string[]>
    show_actions: p.Property<boolean>
    theme: p.Property<string | null>
    throttle: p.Property<any>
  }
}

export interface VegaPlot extends VegaPlot.Attrs {}

export class VegaPlot extends HTMLBox {
  properties: VegaPlot.Props

  constructor(attrs?: Partial<VegaPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vega"

  static {
    this.prototype.default_view = VegaPlotView

    this.define<VegaPlot.Props>(({Any, Array, Boolean, Nullable, String}) => ({
      data:         [ Any,                {} ],
      data_sources: [ Any,                {} ],
      events:       [ Array(String),      [] ],
      show_actions: [ Boolean,         false ],
      theme:        [ Nullable(String), null ],
      throttle:     [ Any,                {} ]
    }))
  }
}
