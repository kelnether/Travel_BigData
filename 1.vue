<template>
  <div ref="chart" style="width:100%; height:300px;"></div>
</template>
<script>
import * as echarts from 'echarts';
import chinaMap from 'echarts/map/json/china.json';
export default {
  name: "MapChart",
  props: { data: Array },  // 传入数据: [{name: '上海', value: 5000}, ...]
  mounted() {
    echarts.registerMap('china', chinaMap);
    const chart = echarts.init(this.$refs.chart);
    const option = {
      series: [{
        type: 'map',
        map: 'china',
        label: { show: true },
        data: this.data
      }]
    };
    chart.setOption(option);
    chart.on('click', params => {
      this.$emit('map-click', params.name);
    });
  }
}
</script>
