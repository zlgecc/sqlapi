<template>
  <div class="main">
    <el-container class="border">
      <el-aside width="200px" class="">
        <el-menu default-active="1">
          <el-sub-menu index="1" unique-opened="true">
            <template #title>
              <span>DB></span>
            </template>
            <!-- <el-menu-item index="1-1">item one</el-menu-item> -->
            <el-menu-item :index="item" v-for="item in tables">{{item}}</el-menu-item>
          </el-sub-menu>

        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="">admin</el-header>

        <el-container>
          <el-table :data="tableData" style="width: 100%; height:100%;">
            <el-table-column prop="date" label="Date" width="180" />
            <el-table-column prop="name" label="Name" width="180" />
            <el-table-column prop="address" label="Address" />
          </el-table>
        </el-container>

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
      tableHead: [],
      tableData: [
        {
          date: "2016-05-03",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-02",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-04",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-01",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-08",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-06",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
        {
          date: "2016-05-07",
          name: "Tom",
          address: "No. 189, Grove St, Los Angeles",
        },
      ],
    });
    // define method
    const methods = {
      getTables() {
        axios.get("/a/admin/tables").then((res) => {
          state.tables = res.data.data
        });
      }
    }
    
    onMounted(() => {
      // do something
      console.log("mounted start...")
      methods.getTables()
    })

    return {
      ...toRefs(state),
      ...methods
    }
  },

};
</script>

<style>
</style>
