var vm = new Vue({
    el:"app",
    data:{
        host,
        error_username:false,
        error_username_message:'请填写手机号或用户名',
        error_pwd_message:'请填写密码',
        username:'',
        password:"",
        remember:false,
    },
    methods:{
        check_username:function () {
            if (!this.username) {
                this.error_username_message = '请填写手机号或用户名';
                this.error_username = true
            }else {
                this.error_username = false;
            }
        },
        check_pwd:function () {
            if (!this.password) {
                            this.error_pwd_message = '请填写手机号或用户名';
                            this.error_password = true
                        }else {
                            this.error_password = false;
                        }
        },
        get_query_string:function(name){
            var reg = new RegExp('(^|&)'+name+'=([^&]*)(&|$)',"i");
            var r = window.location.search.substr(1).match(reg);
            if (r != null){
                return decodeURI(r[2]);
            }
            return null;
        },
        on_submit:function () {
            this.check_username();
            this.check_pwd();

            if (this.error_username == false && this.error_pwd == false){
                axios.post(this.host+'authorizations/',{
                    username:"this.username",
                    password:"this.password"
                },{
                    responseType:'json'
                }).then(response => {
                    if (this.remember)
                    {
                        sessionStorage.clear();
                        localStorage.token = response.data.token;
                        localStorage.username = response.data.username;
                        localStorage.user_id = response.data.id;
                    }else {
                        localStorage.clear();
                        sessionStorage.token = response.data.token;
                        sessionStorage.username = response.data.username;
                        sessionStorage.user_id = response.data.id;
                    }
                    // 判断跳转位置
                    var return_url = this.get_query_string('next');
                    if (!return_url){
                        return_url = '/index.html'
                    }
                    location.href = return_url;

                })
                    .catch(error =>{
                        this.error_pwd_message = "用户名或密码错误";
                        this.error_pwd = true
                    })
            }

        }
    }
})