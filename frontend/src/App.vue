<template>
  <el-config-provider :locale="zhCn">
  <div ref="containerRef" class="container mx-auto py-10 px-4 max-w-5xl min-h-screen touch-pan-y">
    <Card class="w-full bg-transparent border-0 shadow-none">
      <div class="flex flex-col sm:flex-row items-center justify-between mb-6 gap-4">
        <h1 class="text-3xl font-bold tracking-tight text-foreground">备忘录</h1>
        
        <div class="flex items-center gap-2">
          <!-- Category Filter -->
          <div class="flex items-center bg-muted/30 p-1.5 rounded-xl border border-border">
             <button 
               v-for="cat in ['all', 'work', 'life']" 
               :key="cat"
               @click="currentCategory = cat"
               :class="[
                 'px-4 py-2 text-sm font-medium rounded-lg transition-colors min-w-[60px]',
                 currentCategory === cat 
                   ? 'bg-white text-zinc-950 shadow-sm' 
                   : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
               ]"
             >
               {{ cat === 'all' ? '全部' : (cat === 'work' ? '工作' : '生活') }}
             </button>
          </div>
          
          <Button variant="outline" @click="templatesVisible = true" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 gap-2 rounded-lg">
            <LayoutTemplate class="h-4 w-4" />
            模板
          </Button>
        </div>
      </div>
      
      <div v-if="loading && memos.length === 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" v-auto-animate>
        <div v-for="i in 6" :key="i" class="h-48 rounded-lg border bg-card text-card-foreground shadow-sm animate-pulse bg-muted/20"></div>
      </div>

      <div v-else-if="memos.length === 0" class="flex flex-col items-center justify-center py-16 text-center text-muted-foreground border rounded-lg bg-card/50 border-dashed">
        <div class="rounded-full bg-muted/30 p-4 mb-4">
          <Clock class="h-8 w-8 opacity-50" />
        </div>
        <p class="text-lg font-medium">暂无备忘录</p>
        <p class="text-sm mt-1">点击右上角添加第一条备忘</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" v-auto-animate>
        <div 
          v-for="memo in memos" 
          :key="memo.id" 
          class="group relative flex flex-col justify-between rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-200"
        >
          <!-- Card Header -->
          <div class="p-4 pb-2 space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div class="flex flex-col gap-1 min-w-0">
                <div class="flex items-center gap-2">
                   <Badge variant="outline" :class="[
                     'text-[10px] px-1.5 py-0 h-5 border-zinc-200',
                     memo.category === 'work' ? 'bg-yellow-50 text-yellow-600 border-yellow-200' : 'bg-green-50 text-green-600 border-green-200'
                   ]">
                     {{ memo.category === 'work' ? '工作' : '生活' }}
                   </Badge>
                   <h3 class="font-semibold leading-tight tracking-tight line-clamp-1" :title="memo.title">
                     {{ memo.title }}
                   </h3>
                   <span v-if="memo.deadline && !memo.completed_at" :class="getDeadlineClass(memo.deadline)" class="text-[10px] px-1.5 py-0.5 rounded border">
                     {{ getDeadlineText(memo.deadline) }}
                   </span>
                </div>
              </div>
              <Badge :variant="memo.completed_at ? 'default' : 'secondary'" class="shrink-0">
                {{ memo.completed_at ? '已完成' : '进行中' }}
              </Badge>
            </div>
            <p class="text-sm text-muted-foreground line-clamp-4 min-h-[1.25rem]">
              {{ memo.content }}
            </p>
          </div>

          <!-- Subtasks -->
          <div v-if="memo.subtasks && memo.subtasks.length > 0" class="px-4 py-2">
            <div class="space-y-1.5 bg-muted/30 p-2.5 rounded-md text-sm">
              <div 
                v-for="subtask in memo.subtasks" 
                :key="subtask.id" 
                class="flex flex-col"
              >
                <div class="flex items-start gap-2 group/item justify-between">
                  <div class="flex items-start gap-2 flex-1 min-w-0">
                    <Checkbox 
                      :checked="subtask.is_completed" 
                      @update:checked="(val) => handleSubTaskToggle(subtask, val)"
                      class="mt-0.5 h-3.5 w-3.5 shrink-0"
                    />
                    <span :class="{'line-through text-muted-foreground': subtask.is_completed, 'break-all': true, 'text-foreground': !subtask.is_completed}">
                      {{ subtask.content }}
                    </span>
                  </div>
                  <span v-if="subtask.completed_at" class="text-xs text-green-600/80 shrink-0 whitespace-nowrap ml-1">
                    {{ calculateDuration(subtask.created_at, subtask.completed_at) }}
                  </span>
                </div>
                
                <!-- Subtask Note -->
                <div v-if="subtask.note" class="ml-6 mt-1 text-xs text-muted-foreground bg-zinc-50/50 p-1.5 rounded border border-zinc-100/50">
                  <div :class="{'line-clamp-1': !subtask._expanded, 'break-all whitespace-pre-wrap': true}">
                    {{ subtask.note }}
                  </div>
                  <div v-if="subtask.note.length > 20" class="flex justify-end mt-1">
                     <button 
                       @click.stop="subtask._expanded = !subtask._expanded" 
                       class="text-[10px] flex items-center gap-0.5 text-zinc-400 hover:text-zinc-600 transition-colors"
                     >
                       {{ subtask._expanded ? '收起' : '展开' }}
                       <component :is="subtask._expanded ? ChevronUp : ChevronDown" class="h-3 w-3" />
                     </button>
                  </div>
                </div>

                <!-- Subtask Attachments -->
                <div v-if="subtask.attachments && subtask.attachments.length > 0" class="ml-6 mt-1 flex flex-wrap gap-2">
                   <a v-for="att in subtask.attachments" :key="att.id" :href="getAttachmentUrl(att.file_path)" target="_blank" class="flex items-center gap-1 text-[10px] text-zinc-500 bg-zinc-50 border px-1.5 py-0.5 rounded hover:text-zinc-800 hover:bg-zinc-100 transition-colors" @click.stop>
                     <Paperclip class="h-3 w-3" />
                     <span class="max-w-[100px] truncate" :title="att.filename">{{ att.filename }}</span>
                   </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Chart -->
          <div v-if="memo.completed_at && memo.category === 'work'" class="px-4 py-2 border-t border-dashed">
             <MemoPieChart :memo-id="memo.id" />
          </div>

          <!-- Card Footer -->
          <div class="p-4 pt-2 mt-auto">
            <div class="flex items-center justify-between text-xs text-muted-foreground border-t pt-3">
              <div class="space-y-0.5">
                <div class="flex items-center gap-1">
                  <span class="opacity-70">创建:</span>
                  <span>{{ formatDate(memo.created_at).split(' ')[0] }}</span>
                </div>
                <div v-if="memo.completed_at" class="flex items-center gap-1 text-green-600/80">
                  <span class="opacity-70">用时:</span>
                  <span>{{ calculateDuration(memo.created_at, memo.completed_at) }}</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-2 -mr-2">
                <Button 
                  v-if="!memo.completed_at"
                  variant="ghost" 
                  size="icon" 
                  class="h-10 w-10 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-full"
                  @click="handleComplete(memo)"
                  title="完成"
                >
                  <CheckCircle class="h-5 w-5" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  class="h-10 w-10 text-muted-foreground hover:text-foreground rounded-full" 
                  @click="openEditDialog(memo)"
                  title="编辑"
                >
                  <Edit class="h-5 w-5" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  class="h-10 w-10 text-destructive/70 hover:text-destructive hover:bg-destructive/10 rounded-full" 
                  @click="handleDelete(memo.id)"
                  title="删除"
                >
                  <Trash2 class="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Load More / Sentinel -->
      <div class="py-4 text-center text-sm text-muted-foreground">
        <span v-if="loading && memos.length > 0">加载更多...</span>
        <span v-else-if="!hasMore && memos.length > 0">没有更多了</span>
      </div>
    </Card>

    <!-- Floating Action Button -->
    <Button 
      class="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50 p-0" 
      @click="openCreateDialog"
    >
      <Plus class="h-6 w-6" />
    </Button>

    <!-- Rename Attachment Dialog -->
    <DialogRoot v-model:open="renameDialogVisible">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[60] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent class="fixed left-[50%] top-[50%] z-[60] grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg text-zinc-950">
          <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
            重命名附件
          </DialogTitle>
          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">文件名</label>
              <Input v-model="renameForm.newName" placeholder="输入新的文件名" class="bg-white text-zinc-950 border-zinc-200" @keyup.enter="confirmRename" />
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <Button variant="outline" @click="renameDialogVisible = false" class="h-11 px-6 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 rounded-lg text-base">
              取消
            </Button>
            <Button @click="confirmRename" class="h-11 px-6 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 rounded-lg text-base">
              确定
            </Button>
          </div>
          <DialogClose class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground text-zinc-500 hover:text-zinc-900">
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- Memo Dialog -->
    <DialogRoot v-model:open="dialogVisible">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg max-h-[85vh] overflow-y-auto text-zinc-950">
          <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
            {{ isEdit ? '编辑备忘' : '新建备忘' }}
          </DialogTitle>
          
          <input type="file" ref="fileInput" class="hidden" @change="handleFileChange" />
          
          <div class="grid gap-4 py-4">
            <!-- Category Selection -->
            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">分类</label>
              <div class="flex items-center gap-4">
                 <label class="flex items-center gap-2 cursor-pointer">
                   <input type="radio" v-model="form.category" value="work" :disabled="isEdit" class="w-4 h-4 text-zinc-900 border-zinc-300 focus:ring-zinc-900 disabled:opacity-50" />
                   <span class="text-sm" :class="{'opacity-50': isEdit}">工作</span>
                 </label>
                 <label class="flex items-center gap-2 cursor-pointer">
                   <input type="radio" v-model="form.category" value="life" :disabled="isEdit" class="w-4 h-4 text-zinc-900 border-zinc-300 focus:ring-zinc-900 disabled:opacity-50" />
                   <span class="text-sm" :class="{'opacity-50': isEdit}">生活</span>
                 </label>
              </div>
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">标题</label>
              <Input v-model="form.title" placeholder="输入标题" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">内容</label>
              <textarea 
                v-model="form.content" 
                class="flex min-h-[80px] w-full rounded-md border border-input bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-zinc-950 border-zinc-200"
                placeholder="输入内容"
              ></textarea>
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">开始时间</label>
              <DateTimeInput v-model="form.created_at_local" />
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">截止时间</label>
              <DateTimeInput v-model="form.deadline_local" />
            </div>
            
            <!-- Subtasks Section -->
            <div class="grid gap-2">
               <label class="text-sm font-medium leading-none flex justify-between items-center">
                 <span>子待办事项</span>
                 <Button size="sm" variant="outline" @click="addSubTask" type="button" class="h-8 text-xs px-3 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 rounded-lg">
                   <Plus class="h-4 w-4 mr-1" /> 添加
                 </Button>
               </label>
               <draggable 
                 v-model="form.subtasks" 
                 item-key="id"
                 handle=".drag-handle"
                 class="space-y-2 max-h-[300px] overflow-y-auto pr-1"
                 :animation="200"
                 ghost-class="ghost"
                 drag-class="drag"
               >
                 <template #item="{ element: subtask, index }">
                   <div class="flex flex-col gap-2 group bg-white p-2 rounded-md border border-transparent hover:border-zinc-100 transition-colors">
                     <div class="flex items-start gap-2">
                       <div class="drag-handle cursor-grab active:cursor-grabbing text-zinc-400 hover:text-zinc-600 p-2 mt-0.5">
                        <GripVertical class="h-5 w-5" />
                      </div>
                      <Checkbox 
                        v-model:checked="subtask.is_completed" 
                        @update:checked="(val) => { if(val && !subtask.completed_at_local) subtask.completed_at_local = toLocalISOString(new Date().toISOString()) }"
                        class="border-zinc-400 data-[state=checked]:bg-zinc-900 data-[state=checked]:text-zinc-50 shrink-0 mt-3 h-5 w-5" 
                      />
                      <div class="flex-1 flex flex-col min-w-0 gap-1">
                        <Input v-model="subtask.content" class="h-10 text-sm bg-white text-zinc-950 border-zinc-200" placeholder="待办事项内容" />
                        <div class="flex flex-col gap-1 w-full px-1">
                          <div class="flex items-center gap-2">
                            <span class="text-[10px] text-muted-foreground w-8 shrink-0">开始</span>
                            <DateTimeInput v-model="subtask.created_at_local" size="small" />
                          </div>
                          <div v-if="subtask.is_completed" class="flex items-center gap-2">
                            <span class="text-[10px] text-muted-foreground w-8 shrink-0">完成</span>
                            <DateTimeInput v-model="subtask.completed_at_local" size="small" />
                          </div>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon" class="h-10 w-10 text-zinc-400 hover:text-zinc-600 shrink-0 mt-0.5 rounded-full" @click="subtask.showNote = !subtask.showNote" :title="subtask.showNote ? '隐藏附注' : '添加附注'">
                        <MessageSquare class="h-5 w-5" />
                      </Button>
                      <Button variant="ghost" size="icon" class="h-10 w-10 text-zinc-400 hover:text-zinc-600 shrink-0 mt-0.5 rounded-full" @click="triggerFileUpload(subtask)" :title="subtask.id ? '上传附件' : '请先保存后再上传附件'" :disabled="!subtask.id">
                        <Paperclip class="h-5 w-5" />
                      </Button>
                      <Button variant="ghost" size="icon" class="h-10 w-10 text-destructive shrink-0 hover:bg-zinc-100 mt-0.5 rounded-full" @click="removeSubTask(index)">
                        <X class="h-5 w-5" />
                      </Button>
                    </div>
                     
                     <!-- Note Input -->
                     <div v-if="subtask.showNote || subtask.note" class="ml-9 mr-9">
                        <textarea 
                          v-model="subtask.note" 
                          class="flex min-h-[60px] w-full rounded-md border border-input bg-zinc-50 px-3 py-2 text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 text-zinc-950 border-zinc-200"
                          placeholder="添加附注..."
                        ></textarea>
                     </div>
                     
                     <!-- Attachments List -->
                     <div v-if="subtask.attachments && subtask.attachments.length > 0" class="ml-9 mr-9 mt-2 space-y-2">
                        <div v-for="att in subtask.attachments" :key="att.id" class="flex items-center justify-between gap-2 text-sm bg-zinc-50 p-2 rounded-lg border border-zinc-200">
                           <div class="flex items-center gap-2 min-w-0 flex-1">
                             <div class="bg-white p-1.5 rounded border border-zinc-100 shrink-0">
                               <Paperclip class="h-4 w-4 text-zinc-400" />
                             </div>
                             <a :href="getAttachmentUrl(att.file_path)" target="_blank" class="truncate text-zinc-700 font-medium hover:underline">{{ att.filename }}</a>
                           </div>
                           <div class="flex items-center gap-1 shrink-0">
                             <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200/50" @click="renameAttachment(att)" title="重命名">
                               <Pencil class="h-4 w-4" />
                             </Button>
                             <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500 hover:text-red-600 hover:bg-red-50" @click="deleteAttachment(att, subtask)" title="删除">
                               <Trash2 class="h-4 w-4" />
                             </Button>
                           </div>
                        </div>
                     </div>
                   </div>
                 </template>
               </draggable>
               <div v-if="form.subtasks.length === 0" class="text-xs text-muted-foreground text-center py-2 bg-zinc-50 rounded-md border border-dashed border-zinc-200">
                 暂无子待办
               </div>
            </div>

            <div class="grid gap-2" v-if="isEdit">
              <div class="flex items-center space-x-2">
                <Checkbox id="isCompleted" v-model:checked="form.isCompleted" @update:checked="handleStatusChange" class="border-zinc-400 data-[state=checked]:bg-zinc-900 data-[state=checked]:text-zinc-50" />
                <label
                  for="isCompleted"
                  class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  已完成
                </label>
              </div>
            </div>
            
            <div class="grid gap-2" v-if="isEdit && form.isCompleted">
              <label class="text-sm font-medium leading-none">完成时间</label>
              <input 
                type="datetime-local" 
                v-model="form.completed_at_local"
                step="900"
                class="flex h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-zinc-950 border-zinc-200"
              />
            </div>
          </div>
          <div class="flex justify-between items-center mt-6">
            <Button v-if="isEdit" variant="outline" @click="saveAsTemplate" class="h-10 px-4 text-sm gap-2 border-dashed rounded-lg">
              <Copy class="h-4 w-4" /> 存为模板
            </Button>
            <div v-else></div> <!-- Spacer -->
            
            <div class="flex space-x-3">
              <Button variant="outline" @click="dialogVisible = false" class="h-11 px-6 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 rounded-lg text-base">取消</Button>
              <Button @click="handleSubmit" class="h-11 px-6 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 rounded-lg text-base">确定</Button>
            </div>
          </div>
          <DialogClose class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground text-zinc-500 hover:text-zinc-900">
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- Alert Dialog -->
    <AlertDialog v-model:open="alertState.open">
      <AlertDialogContent class="w-[calc(100%-2rem)] max-w-lg gap-6 border bg-white p-6 shadow-lg rounded-lg md:w-full">
        <AlertDialogHeader>
          <AlertDialogTitle class="text-xl font-semibold text-center">{{ alertState.title }}</AlertDialogTitle>
          <AlertDialogDescription class="text-base text-muted-foreground text-center">
            {{ alertState.content }}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter :class="[
          'w-full mt-2',
          alertState.isConfirm ? 'grid grid-cols-2 gap-4' : 'flex justify-center'
        ]">
          <AlertDialogCancel 
            v-if="alertState.isConfirm" 
            @click="onAlertCancel" 
            class="rounded-lg font-medium bg-white text-zinc-950 border border-zinc-200 hover:bg-zinc-100 h-11 px-6 mt-0"
          >
            {{ alertState.cancelText || '取消' }}
          </AlertDialogCancel>
          <AlertDialogAction 
            @click="onAlertConfirm" 
            class="rounded-lg font-medium bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 h-11 px-6"
          >
            {{ alertState.confirmText || '确定' }}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <!-- Templates Dialog -->
    <DialogRoot v-model:open="templatesVisible">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80" />
        <DialogContent class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg sm:rounded-lg max-h-[85vh] overflow-y-auto text-zinc-950">
          <DialogTitle class="text-lg font-semibold">常用模板</DialogTitle>
          
          <div class="my-2">
            <Input v-model="templateSearchQuery" placeholder="搜索模板标题..." class="bg-white text-zinc-950 border-zinc-200" />
          </div>

          <div v-if="templates.length === 0" class="text-center py-8 text-muted-foreground border border-dashed rounded-lg">
            暂无模板，请在编辑备忘录时点击"存为模板"
          </div>
          
          <div v-else-if="filteredTemplates.length === 0" class="text-center py-8 text-muted-foreground border border-dashed rounded-lg">
            未找到匹配的模板
          </div>

          <div v-else class="space-y-3">
             <div v-for="temp in filteredTemplates" :key="temp.id" class="flex items-start justify-between p-3 border rounded-lg bg-zinc-50/50 hover:bg-zinc-50 transition-colors">
                <div class="space-y-1 min-w-0 flex-1">
                   <div class="flex items-center gap-2">
                      <Badge variant="outline" class="text-[10px] px-1 py-0 h-4" :class="{
                        'bg-yellow-100 text-yellow-800 border-yellow-200': temp.category === 'work',
                        'bg-green-100 text-green-800 border-green-200': temp.category === 'life'
                      }">{{ temp.category === 'work' ? '工作' : '生活' }}</Badge>
                      <h4 class="font-medium text-sm truncate">{{ temp.title }}</h4>
                   </div>
                   <p class="text-xs text-muted-foreground line-clamp-2">{{ temp.content }}</p>
                   <p class="text-[10px] text-muted-foreground">{{ temp.subtasks.length }} 个子任务</p>
                </div>
                <div class="flex items-center gap-2 ml-2 shrink-0">
                   <Button size="sm" variant="secondary" class="h-9 px-3 text-xs rounded-lg" @click="useTemplate(temp)">
                     使用
                   </Button>
                   <Button size="icon" variant="ghost" class="h-9 w-9 text-destructive/70 hover:text-destructive rounded-full" @click="deleteTemplate(temp.id)">
                     <Trash2 class="h-4 w-4" />
                   </Button>
                </div>
             </div>
          </div>

          <div class="flex justify-end">
            <Button variant="outline" @click="templatesVisible = false">关闭</Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useInfiniteScroll, useSwipe } from '@vueuse/core';
import api from './api';
import { ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import DateTimeInput from '@/components/DateTimeInput.vue';
import MemoPieChart from '@/components/MemoPieChart.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Card from '@/components/ui/card/Card.vue';
import CardHeader from '@/components/ui/card/CardHeader.vue';
import CardContent from '@/components/ui/card/CardContent.vue';
import Badge from '@/components/ui/badge/Badge.vue';
import Checkbox from '@/components/ui/checkbox/Checkbox.vue';
import { 
  DialogRoot, 
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogClose,
} from 'radix-vue';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';
import { Plus, Trash2, Edit, CheckCircle, Clock, ChevronDown, ChevronUp, GripVertical, MessageSquare, X, LayoutTemplate, Copy, Paperclip, Pencil } from 'lucide-vue-next';
import draggable from 'vuedraggable';

// State
const memos = ref([]);
const loading = ref(false);
const page = ref(0);
const hasMore = ref(true);
const dialogVisible = ref(false);
const isEdit = ref(false);
const currentId = ref(null);
const currentCategory = ref('all'); // 'all', 'work', 'life'
const templates = ref([]);
const templatesVisible = ref(false);
const templateSearchQuery = ref('');

// Swipe Navigation
const containerRef = ref(null);
const { direction, isSwiping, lengthX } = useSwipe(containerRef);

watch(isSwiping, (newVal) => {
  if (!newVal) { // Swiping ended
    const threshold = 50; // Minimum distance
    if (Math.abs(lengthX.value) > threshold) {
      const categories = ['all', 'work', 'life'];
      const currentIndex = categories.indexOf(currentCategory.value);
      
      if (direction.value === 'left') {
        // Next category (Swipe Left -> Go Right)
        if (currentIndex < categories.length - 1) {
          currentCategory.value = categories[currentIndex + 1];
        }
      } else if (direction.value === 'right') {
        // Previous category (Swipe Right -> Go Left)
        if (currentIndex > 0) {
          currentCategory.value = categories[currentIndex - 1];
        }
      }
    }
  }
});

// Alert State
const alertState = ref({
  open: false,
  title: '',
  content: '',
  isConfirm: false,
  resolve: null,
  cancelText: '取消',
  confirmText: '确定'
});

const showAlert = (message, title = '提示') => {
  return new Promise((resolve) => {
    alertState.value = {
      open: true,
      title,
      content: message,
      isConfirm: false,
      resolve,
      cancelText: '取消',
      confirmText: '确定'
    };
  });
};

const showConfirm = (message, title = '确认', confirmText = '确定', cancelText = '取消') => {
  return new Promise((resolve) => {
    alertState.value = {
      open: true,
      title,
      content: message,
      isConfirm: true,
      resolve,
      confirmText,
      cancelText
    };
  });
};

const onAlertConfirm = () => {
  alertState.value.open = false;
  if (alertState.value.resolve) alertState.value.resolve(true);
};

const onAlertCancel = () => {
  alertState.value.open = false;
  if (alertState.value.resolve) alertState.value.resolve(false);
};

const filteredTemplates = computed(() => {
  if (!templateSearchQuery.value.trim()) return templates.value;
  const query = templateSearchQuery.value.toLowerCase().trim();
  return templates.value.filter(t => t.title.toLowerCase().includes(query));
});

const form = ref({
  title: '',
  content: '',
  isCompleted: false,
  subtasks: [],
  created_at_local: '',
  completed_at_local: '',
  category: 'work'
});

// Helper to format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const toLocalISOString = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  const localDate = new Date(date.getTime() - offsetMs);
  return localDate.toISOString().slice(0, 16);
};

// Calculate duration
const calculateDuration = (start, end) => {
  if (!start || !end) return '';
  const startTime = new Date(start);
  const endTime = new Date(end);
  const diff = endTime - startTime;
  
  if (diff < 0) return '0分';
  
  const minutes = Math.floor(diff / 1000 / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}天${hours % 24}小时`;
  if (hours > 0) return `${hours}小时${minutes % 60}分`;
  return `${minutes}分`;
};

const getDeadlineText = (deadline) => {
  if (!deadline) return '';
  const now = new Date();
  const end = new Date(deadline);
  const diff = end - now;
  
  if (diff < 0) {
    const days = Math.floor(Math.abs(diff) / (1000 * 60 * 60 * 24));
    return days === 0 ? '已逾期' : `逾期 ${days} 天`;
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days === 0) return '今天到期';
  return `剩余 ${days} 天`;
};

const getDeadlineClass = (deadline) => {
  if (!deadline) return '';
  const now = new Date();
  const end = new Date(deadline);
  const diff = end - now;
  
  if (diff < 0) return 'bg-red-50 text-red-600 border-red-200'; // Overdue
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days <= 2) return 'bg-orange-50 text-orange-600 border-orange-200'; // Urgent
  return 'bg-blue-50 text-blue-600 border-blue-200'; // Normal
};

// Fetch memos
const fetchMemos = async (isLoadMore = false) => {
  if (loading.value) return;
  if (!isLoadMore) {
    page.value = 0;
    memos.value = [];
    hasMore.value = true;
  }
  
  if (!hasMore.value) return;
  
  loading.value = true;
  try {
    const params = {
      skip: page.value * 12,
      limit: 12
    };
    if (currentCategory.value !== 'all') {
      params.category = currentCategory.value;
    }
    
    const response = await api.get('/memos/', { params });
    const newMemos = response.data;
    
    if (newMemos.length < 12) {
      hasMore.value = false;
    }
    
    const processedMemos = newMemos.map(memo => ({
      ...memo,
      subtasks: memo.subtasks.map(st => ({
        ...st,
        _expanded: false
      }))
    }));

    if (isLoadMore) {
      memos.value.push(...processedMemos);
    } else {
      memos.value = processedMemos;
    }
    page.value++;
  } catch (error) {
    console.error('Failed to fetch memos:', error);
  } finally {
    loading.value = false;
  }
};

// Fetch templates
const fetchTemplates = async () => {
  try {
    const response = await api.get('/templates/');
    templates.value = response.data;
  } catch (error) {
    console.error('Failed to fetch templates:', error);
  }
};

// Save as template
const saveAsTemplate = async () => {
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      category: form.value.category,
      subtasks: form.value.subtasks.map(st => ({
        content: st.content,
        order: st.order || 0
      }))
    };
    
    await api.post('/templates/', payload);
    showAlert('已保存为模板');
    fetchTemplates();
  } catch (error) {
    console.error('Failed to save template:', error);
    showAlert('保存模板失败');
  }
};

// Use template
const useTemplate = (template) => {
  form.value = {
    title: template.title,
    content: template.content,
    isCompleted: false,
    subtasks: template.subtasks.map(st => ({
      ...st,
      id: undefined, // Clear ID for new subtasks
      is_completed: false,
      showNote: false,
      note: '',
      created_at_local: toLocalISOString(new Date().toISOString()),
      completed_at_local: ''
    })),
    created_at_local: toLocalISOString(new Date().toISOString()),
    completed_at_local: '',
    category: template.category
  };
  templatesVisible.value = false;
  dialogVisible.value = true;
  isEdit.value = false;
  currentId.value = null;
};

// Delete template
const deleteTemplate = async (id) => {
  if (!confirm('确定删除该模板吗？')) return;
  try {
    await api.delete(`/templates/${id}`);
    fetchTemplates();
  } catch (error) {
    console.error('Failed to delete template:', error);
  }
};

// Watch category change
watch(currentCategory, () => {
  fetchMemos(false);
});

// Dialog methods
const openCreateDialog = async () => {
  // Check for templates
  if (templates.value.length > 0) {
     if (await showConfirm('是否使用已有模板？', '新建备忘', '使用模板', '直接创建')) {
        templatesVisible.value = true;
        return;
     }
  }

  isEdit.value = false;
  currentId.value = null;
  form.value = {
    title: '',
    content: '',
    isCompleted: false,
    subtasks: [],
    created_at_local: toLocalISOString(new Date().toISOString()),
    completed_at_local: '',
    deadline_local: '',
    category: 'work' // Default to work
  };
  dialogVisible.value = true;
};

const openEditDialog = (memo) => {
  isEdit.value = true;
  currentId.value = memo.id;
  form.value = {
    title: memo.title,
    content: memo.content,
    isCompleted: !!memo.completed_at,
    subtasks: memo.subtasks ? memo.subtasks.map(st => ({
      ...st,
      showNote: !!st.note,
      created_at_local: st.created_at ? toLocalISOString(st.created_at) : '',
      completed_at_local: st.completed_at ? toLocalISOString(st.completed_at) : ''
    })) : [],
    created_at_local: memo.created_at ? toLocalISOString(memo.created_at) : '',
    completed_at_local: memo.completed_at ? toLocalISOString(memo.completed_at) : '',
    deadline_local: memo.deadline ? toLocalISOString(memo.deadline) : '',
    category: memo.category || 'work'
  };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      category: form.value.category,
      created_at: form.value.created_at_local ? new Date(form.value.created_at_local).toISOString() : null,
      deadline: form.value.deadline_local ? new Date(form.value.deadline_local).toISOString() : null,
      subtasks: form.value.subtasks.map(st => ({
          id: st.id, // Keep ID if exists
          content: st.content,
          note: st.note,
          is_completed: st.is_completed,
          created_at: st.created_at_local ? new Date(st.created_at_local).toISOString() : null,
          completed_at: st.is_completed && st.completed_at_local ? new Date(st.completed_at_local).toISOString() : null
        }))
    };

    if (isEdit.value && form.value.isCompleted) {
       payload.completed_at = form.value.completed_at_local ? new Date(form.value.completed_at_local).toISOString() : (new Date().toISOString());
    } else if (isEdit.value && !form.value.isCompleted) {
       payload.completed_at = null;
    }

    if (isEdit.value) {
      await api.put(`/memos/${currentId.value}`, payload);
      // Update local status if just completed
      if (form.value.isCompleted) {
         await api.patch(`/memos/${currentId.value}/status`, { is_completed: true });
      }
    } else {
      await api.post('/memos/', payload);
    }
    
    dialogVisible.value = false;
    fetchMemos();
  } catch (error) {
    console.error('Operation failed:', error);
  }
};

const handleSubTaskToggle = async (subtask, isChecked) => {
  try {
    // Optimistic update
    subtask.is_completed = isChecked;
    
    // Call API to update status
    await api.patch(`/subtasks/${subtask.id}/status`, {
      is_completed: isChecked
    });
    
    // Refresh to get updated times
    fetchMemos(); 
  } catch (error) {
    console.error('Failed to update subtask:', error);
    // Revert on error
    subtask.is_completed = !isChecked;
  }
};

const handleDelete = async (id) => {
  if (!await showConfirm('确定删除该备忘录吗？')) return;
  try {
    await api.delete(`/memos/${id}`);
    fetchMemos();
  } catch (error) {
    console.error('Failed to delete memo:', error);
  }
};

const handleComplete = async (memo) => {
  if (memo.subtasks && memo.subtasks.length > 0) {
    const hasIncomplete = memo.subtasks.some(st => !st.is_completed);
    if (hasIncomplete) {
      showAlert('该备忘录下有未完成的子任务，无法标记为完成');
      return;
    }
  }

  try {
    await api.patch(`/memos/${memo.id}/status`, {
      is_completed: true
    });
    fetchMemos();
  } catch (error) {
    console.error('Failed to complete memo:', error);
    if (error.response && error.response.data && error.response.data.detail) {
      showAlert(error.response.data.detail);
    }
  }
};

const addSubTask = () => {
  form.value.subtasks.push({
    content: '',
    is_completed: false,
    showNote: false,
    note: '',
    created_at_local: toLocalISOString(new Date().toISOString()),
    completed_at_local: ''
  });
};

const removeSubTask = (index) => {
  form.value.subtasks.splice(index, 1);
};

// Attachment handling
const fileInput = ref(null);
const currentSubtaskForUpload = ref(null);
const renameDialogVisible = ref(false);
const renameForm = ref({
  attachment: null,
  newName: ''
});

const triggerFileUpload = (subtask) => {
  if (!subtask.id) {
    showAlert('请先保存备忘录，然后再上传附件');
    return;
  }
  currentSubtaskForUpload.value = subtask;
  fileInput.value.click();
};

const handleFileChange = async (event) => {
  const file = event.target.files[0];
  if (!file || !currentSubtaskForUpload.value) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post(`/subtasks/${currentSubtaskForUpload.value.id}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // Add the new attachment to the subtask's attachment list locally
    if (!currentSubtaskForUpload.value.attachments) {
      currentSubtaskForUpload.value.attachments = [];
    }
    currentSubtaskForUpload.value.attachments.push(response.data);
    
    showAlert('附件上传成功');
  } catch (error) {
    console.error('Failed to upload attachment:', error);
    showAlert('附件上传失败');
  } finally {
    // Reset file input
    event.target.value = '';
    currentSubtaskForUpload.value = null;
  }
};

const deleteAttachment = async (attachment, subtask) => {
    if (!await showConfirm('确定删除该附件吗？')) return;
    try {
        await api.delete(`/attachments/${attachment.id}`);
        // Remove locally
        const index = subtask.attachments.indexOf(attachment);
        if (index > -1) {
            subtask.attachments.splice(index, 1);
        }
    } catch (error) {
        console.error('Failed to delete attachment:', error);
        showAlert('删除附件失败');
    }
};

const renameAttachment = (attachment) => {
    renameForm.value.attachment = attachment;
    renameForm.value.newName = attachment.filename;
    renameDialogVisible.value = true;
};

const confirmRename = async () => {
    const { attachment, newName } = renameForm.value;
    if (!attachment || !newName || newName.trim() === '' || newName === attachment.filename) {
        renameDialogVisible.value = false;
        return;
    }

    try {
        const response = await api.put(`/attachments/${attachment.id}`, {
            filename: newName
        });
        
        // Update local
        attachment.filename = response.data.filename;
        renameDialogVisible.value = false;
        showAlert('附件重命名成功');
    } catch (error) {
        console.error('Failed to rename attachment:', error);
        showAlert('重命名附件失败');
    }
};

const getAttachmentUrl = (path) => {
  return `${api.defaults.baseURL}/uploads/${path}`;
};

onMounted(() => {
  fetchMemos();
  fetchTemplates();
});

useInfiniteScroll(window, () => {
  if (!loading.value && hasMore.value) {
    fetchMemos(true);
  }
}, { distance: 50 });
</script>
