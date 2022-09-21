<template>
  <el-container>
    <!-- header -->
    <el-header class='bg-white shadow'>
        <div class="menu-header"> Table 管理 </div>
    </el-header>
    <!-- dialog -->
    <el-dialog title="保存数据" top="10px" height="80px" width="30%" v-model="dialogVisible" style="">
      <el-form >
        <div class="data-item" v-for="(item, index) in Object.keys(form)">
          <div v-if="item!='id'">
            <div class='txt-blue'>{{item}}</div>
            <el-input class="txt-gray" v-model="form[item]" autocomplete="off"></el-input>
          </div>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="saveData">确 定</el-button>
        <el-button @click="dialogVisible=false">取 消</el-button>
      </div>
    </el-dialog>

    <!-- body -->
    <el-container style="width: 90%; margin: 0 auto">
      <!-- aside -->
      <el-aside width="200px" class="aside-menu">
        <el-menu>
          <el-menu-item v-for="(item, index) in tables" :index="index" @click="currentTable=item; loadTable()" >{{item}}</el-menu-item>
        </el-menu>
      </el-aside>
      <!-- content -->
      <el-container>
        <div class='radius bg-red center p1'>{{currentTable}}</div>
        <!-- table -->
        <el-table :data="tableData" class="data-table shadow">
          <el-table-column v-for="label in tableHead" :fixed="label == 'id'" :prop="label" :label="label" :show-overflow-tooltip="true" :min-width="dynamic_width(label)" />
          <el-table-column fixed="right" label="操作" width="80">
            <template #default="scope">
              <el-button type="text" size="small" @click="dialogVisible=true;form=scope.row">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- footer -->
        <el-footer class="footer">
          <el-pagination layout="prev, pager, next" :total="page.total" :page-size="page.size" @current-change="loadTable"/>
        </el-footer>
      </el-container>

    </el-container>
  </el-container>
</template>

<script>
import { reactive, onMounted, toRefs, nextTick } from "vue";
import { ElMessage } from 'element-plus';
import axios from "axios";

export default {
  setup() {
    const state = reactive({
      tables: [],
      currentTable: "Admin",
      tableHead: ['id'],
      tableData: [],
      page: {size: 20, total: 1, pageNum: 1},
      dialogVisible: false,
      form: {}
    });
    // define method
    const methods = {
      getTablesMenu() {
        axios.get("/api/tables").then((res) => {
          state.tables = res.data.data
          state.currentTable = state.tables[0]
          nextTick(() => document.querySelector(".el-menu-item").click());
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
      },
      dynamic_width(text) {
        let max_width = 180;
        let min_width = 20;
        let dw = text.length*27 
        dw = dw > max_width ? max_width : dw
        dw = dw < min_width ? min_width : dw
        return dw
      },
      saveData() {
        const id = state.form['id'];
        const url =`/api/${state.currentTable}?id=${id}`

        const data = Object.assign({}, state.form);
        delete data['id']
        axios.put(url, JSON.stringify(data)).then((res) => {
          ElMessage({ message: 'success', type: 'success' });
          methods.loadTable(state.page.pageNum)
        })
        state.dialogVisible = false
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
</style>
