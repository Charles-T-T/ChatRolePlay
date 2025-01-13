> [!TIP]
>
> 这里存放各种工具/功能的测试/评估代码
>
> 如果要在这里调试 `ChatRolePlay` ，记得先调整工作路径：
>
> ```python
> import os
> 
> if not "ChatRolePlay" in os.listdir(os.getcwd()):
>        os.chdir("..")
> ```
>
> 然后再
>
> ```python
> from ChatRolePlay import ChatRolePlay
> ```