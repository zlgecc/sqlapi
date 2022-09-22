<template>
  <el-container>
    <!-- header -->
    <el-header class='bg-white shadow'>
      <div class="menu-header"> Table 管理 </div>
    </el-header>
    <!-- dialog -->
    <el-dialog title="详情" top="10px" height="80px" width="30%" v-model="dialogVisible" style="">
      <el-form>
        <div class="data-item" v-for="(item, index) in Object.keys(form)">
          <div v-if="item!='id'">
            <div class='txt-blue'>{{item}}</div>
            <el-input v-model="form[item]" autocomplete="off"></el-input>
          </div>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="saveData">保 存</el-button>
        <el-button @click="dialogVisible=false">取 消</el-button>
      </div>
    </el-dialog>

    <!-- body -->
    <el-container style="width: 90%; margin: 0 auto">
      <!-- aside -->
      <el-aside width="200px" class="aside-menu">
        <el-menu>
          <el-menu-item v-for="(item, index) in tables" :index="index" @click="currentTable=item; loadTable()">{{item}}</el-menu-item>
        </el-menu>
      </el-aside>
      <!-- content -->
      <el-container>
        <div class='radius bg-red txt-center p1'>
          {{currentTable}}
        </div>
        <!-- search -->
        <div class="p1">
          <div class="operator">
            <el-button round size="small" class="shadow" @click="openDialog(false)">新增</el-button>
            <el-button round type="primary" size="small" class=" shadow" @click="searchData">搜索</el-button>
          </div>

          <div class="search-item" v-for="(item, index) in searchItems">
            <div class="search-key">
              <el-input v-model="item.key" size="small" autocomplete="off"></el-input>
            </div>
            <div>=</div>
            <div class="search-value">
              <el-input v-model="item.value" size="small" autocomplete="off"></el-input>
            </div>
            <div>
              <el-button round size="small" type='success' @click="searchItemAdd">add</el-button>
              <el-button round size="small" type='danger' @click="searchItems.splice(index, 1)">del</el-button>
            </div>
          </div>
        </div>
        <!-- table -->
        <el-table :data="tableData" class="data-table shadow">
          <el-table-column v-for="label in tableHead" :fixed="label == 'id'" :prop="label" :label="label" :show-overflow-tooltip="true" :min-width="dynamic_width(label)" />
          <el-table-column fixed="right" label="操作" width="80">
            <template #default="scope">
              <el-button type="text" size="small" @click="openDialog(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- footer -->
        <el-footer class="footer">
          <el-pagination layout="prev, pager, next" :total="page.total" :page-size="page.size" @current-change="loadTable" />
        </el-footer>
      </el-container>

    </el-container>
  </el-container>
</template>

<script>
import { reactive, onMounted, toRefs, nextTick } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";

export default {
  setup() {
    const state = reactive({
      tableInfo: {},
      tables: [],
      currentTable: "",
      tableHead: [],
      tableData: [],
      page: { size: 20, total: 1, pageNum: 1 },
      dialogVisible: false,
      form: {},
      searchItems: [],
    });

    // onMounted
    onMounted(() => {
      // do something
      console.log("mounted start...");
      methods.getTablesMenu();

      document.addEventListener("keydown", methods.keyboardShortcuts);
    });
    // define method
    const methods = {
      keyboardShortcuts(e) {
        if (e.keyCode === 13) {
          methods.searchData();
        }
      },
      getTablesMenu() {
        axios.get("/api/tables").then((res) => {
          const responseData = res.data.data;
          state.tableInfo = responseData;
          state.tables = Object.keys(responseData);
          state.currentTable = state.tables[0];
          nextTick(() => document.querySelector(".el-menu-item").click());
        });
      },
      setTable(data, total) {
        if (data.length > 0) {
          state.tableHead = Object.keys(data[0]);
        } else {
          state.tableHead = state.tableInfo[state.currentTable].map(
            (i) => i["name"]
          );
        }
        state.tableData = data;
        state.page.total = total;
      },
      loadTable(pageNum) {
        const url = `/api/${state.currentTable}`;
        let params = {
          page: pageNum ? pageNum : state.page.pageNum,
          size: state.page.size,
          meta: "total",
        };
        state.searchItems.map((item) => {
          params[item["key"]] = item["value"];
        });
        console.log(url, params);
        axios.get(url, { params: params }).then((res) => {
          const total = res.data.data.meta.total;
          const data = res.data.data.list;
          methods.setTable(data, total);
        });
      },
      dynamic_width(text) {
        let max_width = 180;
        let min_width = 20;
        let dw = text.length * 27;
        dw = dw > max_width ? max_width : dw;
        dw = dw < min_width ? min_width : dw;
        return dw;
      },
      openDialog(data) {
        state.dialogVisible=true;
        if (data) {
          state.form = data;
        } else {
          let data = {}
          state.tableHead.map(item => {
            data[item] = '';
          })
          state.form = data;
        }
      },
      saveData() {
        const id = state.form["id"];
        if (id) {
          const url = `/api/${state.currentTable}?id=${id}`;
          const data = Object.assign({}, state.form);
          delete data["id"];
          axios.put(url, JSON.stringify(data)).then((res) => {
            ElMessage({ message: "success", type: "success" });
            methods.loadTable(state.page.pageNum);
          });
        } else {
          const url = `/api/${state.currentTable}`;
          const data = Object.assign({}, state.form);
          delete data["id"];
          Object.keys(data).map(item => {
            if (data[item] == "") {
              delete data[item];
            }
          })
          if (Object.keys(data).length == 0) {
            ElMessage({ message: "数据为空", type: "error" });
            return false;
          }
          axios.post(url, JSON.stringify(data)).then((res) => {
            ElMessage({ message: "success", type: "success" });
            methods.loadTable(state.page.pageNum);
          });
        }

        state.dialogVisible = false;
      },

      searchData() {
        if (state.searchItems.length > 0) {
          methods.loadTable(1);
        } else {
          methods.searchItemAdd();
        }
      },
      searchItemAdd() {
        state.searchItems.push({ key: "", value: "" });
      },
    };

    return {
      ...toRefs(state),
      ...methods,
    };
  },
};
</script>

<style scoped>
</style>
