<template>
  <div class="main">
    <el-container class="border">
      <el-aside width="200px" class="">
        <el-menu default-active="1">
          <div style="height:50px; line-height:50px; text-align:center"> DB.tables </div>
          <el-menu-item :index="item" v-for="item in tables" @click="currentTable=item; loadTable()">{{item}}</el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="">{{currentTable}}</el-header>
        <el-container class="left-border">
          <el-table :data="tableData"  style="height:75vh;">
            <el-table-column v-for="label in tableHead" :prop="label" :label="label" :width="50+label.length*10" align="center"/>
          </el-table>
        </el-container>
        <el-footer class="footer">
          <el-pagination layout="prev, pager, next" :total="page.total" :page-size="page.size" @current-change="loadTable"/>
        </el-footer>
      </el-container>

    </el-container>
  </div>
</template>

<script>
import { reactive, onMounted, toRefs } from "vue";
import axios from "axios";

export default {
  setup() {
    const state = reactive({
      tables: [],
      currentTable: "Admin",
      tableHead: ['id'],
      tableData: [],
      page: {size: 20, total: 1, pageNum: 1}
    });
    // define method
    const methods = {
      getTablesMenu() {
        axios.get("/api/tables").then((res) => {
          state.tables = res.data.data
        });
      },
      setTable(head, data, total) {
        state.tableHead = head
        state.tableData = data
        state.page.total = total
      },
      loadTable(pageNum) {
        const url =`/api/${state.currentTable}`
        const params = {
          page: pageNum? pageNum: state.page.pageNum,
          size: state.page.size,
          meta: "total"
        }
        console.log(url, params)
        axios.get(url, {params: params}).then((res) => {
          const total = res.data.data.meta.total
          const data = res.data.data.list
          if(data.length > 0) {
            methods.setTable(Object.keys(data[0]), data, total)
          } else {
            methods.setTable(["id"], [], 0)
          }
        })
      }
    }
    
    onMounted(() => {
      // do something
      console.log("mounted start...")
      methods.getTablesMenu()
    })

    return {
      ...toRefs(state),
      ...methods
    }
  },

};
</script>

<style scoped>
.el-menu-item{
  height: 35px;
  border-bottom: 1px solid;
}
.left-border {
  border-left: 1px solid;
}
.footer {
  display: flex;
  flex-direction: row-reverse;
  padding-right: 20px;
}
</style>
