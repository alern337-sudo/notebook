<template>
  <el-config-provider :locale="zhCn">
    <div class="flex h-screen w-full bg-zinc-50 dark:bg-zinc-950 text-zinc-950 font-sans">
      <!-- Left Sidebar -->
      <aside class="w-64 border-r bg-white dark:bg-zinc-900 hidden md:flex flex-col shrink-0 z-20">
        <!-- Logo Area -->
        <div class="h-16 flex items-center px-6 border-b shrink-0">
          <span class="text-lg font-bold tracking-tight">Notebook</span>
        </div>
        
        <!-- Nav Links -->
        <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
          <button 
            @click="currentTab = 'memos'"
            :class="['w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors', currentTab === 'memos' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50']"
          >
            <LayoutTemplate class="h-4 w-4" />
            备忘录
          </button>
          <button 
            @click="currentTab = 'consumables'"
            :class="['w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors', currentTab === 'consumables' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50']"
          >
            <CheckCircle class="h-4 w-4" />
            消耗品
          </button>
        </nav>
      </aside>

      <!-- Mobile Sidebar (Sheet) -->
      <DialogRoot v-model:open="mobileMenuOpen">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-black/80 md:hidden data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
          <DialogContent class="fixed left-0 top-0 bottom-0 z-50 w-[280px] border-r bg-white p-6 shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left md:hidden flex flex-col gap-0">
             <div class="h-10 flex items-center mb-6">
               <span class="text-lg font-bold tracking-tight">Notebook</span>
             </div>
             
             <nav class="flex-1 space-y-2">
              <button 
                @click="currentTab = 'memos'; mobileMenuOpen = false"
                :class="['w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors', currentTab === 'memos' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50']"
              >
                <LayoutTemplate class="h-4 w-4" />
                备忘录
              </button>
              <button 
                @click="currentTab = 'consumables'; mobileMenuOpen = false"
                :class="['w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors', currentTab === 'consumables' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50']"
              >
                <CheckCircle class="h-4 w-4" />
                消耗品
              </button>
             </nav>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>

      <!-- Right Main Area -->
      <main class="flex-1 flex flex-col min-w-0 bg-white relative">
        <!-- Header -->
        <header class="h-16 border-b bg-white/80 backdrop-blur-md sticky top-0 z-10 px-4 md:px-6 flex items-center justify-between shrink-0">
          <!-- Mobile Menu Trigger & Title -->
          <div class="flex items-center gap-3 md:gap-4">
             <!-- Mobile Menu Trigger -->
             <Button variant="ghost" size="icon" class="md:hidden -ml-2" @click="mobileMenuOpen = true">
                <Menu class="h-5 w-5" />
             </Button>
             <h1 class="text-lg font-semibold text-zinc-900 truncate max-w-[120px] md:max-w-none">
               {{ currentTab === 'memos' ? '备忘录' : '消耗品' }}
             </h1>
          </div>

          <!-- Actions Area -->
          <div class="flex items-center gap-2 md:gap-3">
             <div v-if="currentTab === 'memos'" class="flex items-center gap-2">
                <!-- Category Filter moved to Header for better access -->
                <div class="hidden md:flex items-center bg-muted/30 p-1 rounded-lg border border-border h-9 md:h-10">
                   <button 
                     v-for="cat in ['all', 'work', 'life']" 
                     :key="cat"
                     @click="currentCategory = cat"
                     :class="[
                       'px-3 md:px-4 py-1 md:py-1.5 text-xs md:text-sm font-medium rounded-md transition-colors',
                       currentCategory === cat 
                         ? 'bg-white text-zinc-950 shadow-sm' 
                         : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                     ]"
                   >
                     {{ cat === 'all' ? '全部' : (cat === 'work' ? '工作' : '生活') }}
                   </button>
                </div>

                <Button variant="outline" size="sm" @click="templatesVisible = true" class="hidden md:flex h-9 px-3 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 gap-2 rounded-lg">
                  <LayoutTemplate class="h-4 w-4" />
                  <span class="hidden lg:inline">模板</span>
                </Button>
             </div>
             
             <!-- Add New Button -->
             <Button @click="openDialog($event)" class="hidden md:flex h-8 md:h-9 px-3 md:px-4 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 shadow-sm rounded-lg gap-2">
               <Plus class="h-4 w-4" />
               <span class="hidden sm:inline">新建</span>
             </Button>
          </div>
        </header>

        <!-- Scrollable Content Area -->
        <div ref="containerRef" class="flex-1 overflow-auto p-4 sm:p-6 pb-32 sm:pb-10 touch-pan-y">
          <Transition name="page-fade" mode="out-in">
          <!-- Content for Memos -->
          <div v-if="currentTab === 'memos'" key="memos" class="max-w-7xl mx-auto">
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
          @click="openEditDialog(memo, $event)"
          class="group relative flex flex-col justify-between rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
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
                </div>
              </div>
              <Badge :variant="memo.completed_at ? 'default' : 'secondary'" class="shrink-0">
                {{ memo.completed_at ? '已完成' : '进行中' }}
              </Badge>
            </div>
            
            <!-- Deadline and Remaining Time (Top) -->
            <div class="flex items-center gap-1.5 text-sm text-muted-foreground mt-1 mb-2 flex-nowrap overflow-hidden" v-if="!memo.completed_at">
               <div class="flex items-center gap-1 font-bold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 text-[clamp(10px,3.5vw,0.75rem)] whitespace-nowrap shrink-0" :class="{'text-red-600 bg-red-50 border-red-200': memo.deadline && getRemainingTime(memo.deadline) === '已过期'}">
                  <Clock class="h-3.5 w-3.5 shrink-0" />
                  <span>{{ memo.deadline ? getRemainingTime(memo.deadline) : '∞' }}</span>
               </div>
               <div 
                 @click.stop="openMemoDeadlinePicker(memo, $event)"
                 @touchstart.stop="handleDeadlineTouchStart(memo)"
                 @touchend.stop="handleDeadlineTouchEnd"
                 @touchmove.stop="handleDeadlineTouchEnd"
                 @touchcancel.stop="handleDeadlineTouchEnd"
                 @mousedown.stop="handleDeadlineTouchStart(memo)"
                 @mouseup.stop="handleDeadlineTouchEnd"
                 @mouseleave.stop="handleDeadlineTouchEnd"
                 @contextmenu.prevent
                 class="flex items-center gap-1 font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 cursor-pointer hover:bg-blue-100 transition-colors text-[clamp(10px,3.5vw,0.75rem)] select-none whitespace-nowrap shrink-0"
               >
                  <CalendarIcon class="h-3.5 w-3.5 shrink-0" />
                  <span>{{ memo.deadline ? formatDate(memo.deadline) : 'FREE' }}</span>
               </div>
            </div>

            <p class="text-sm text-muted-foreground line-clamp-4 min-h-[1.25rem]">
              {{ memo.content }}
            </p>
          </div>

          <!-- Subtasks Toggle -->
          <div v-if="memo.subtasks && memo.subtasks.length > 0" class="px-4 pt-2 pb-0">
             <button @click.stop="memo._showSubtasks = !memo._showSubtasks" class="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors">
                <component :is="memo._showSubtasks ? ChevronUp : ChevronDown" class="h-3 w-3" />
                {{ memo._showSubtasks ? '隐藏子任务' : `查看 ${memo.subtasks.length} 个子任务` }}
             </button>
          </div>

          <!-- Subtasks -->
          <Transition 
            name="expand"
            @enter="onExpandEnter" 
            @after-enter="onExpandAfterEnter" 
            @leave="onExpandLeave"
            :css="false"
          >
            <div v-if="memo.subtasks && memo.subtasks.length > 0 && memo._showSubtasks" class="px-4 py-2">
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
                    <!-- Duration Display -->
                    <span v-if="getSubtaskDuration(subtask)" class="text-green-600 text-xs ml-auto shrink-0 whitespace-nowrap pt-0.5">
                      {{ getSubtaskDuration(subtask) }}
                    </span>
                  </div>
                </div>
                
                <!-- Subtask Note -->
                <div v-if="subtask.note" 
                     class="ml-6 mt-1 text-xs text-muted-foreground bg-zinc-50/50 p-1.5 rounded border border-zinc-100/50 transition-all cursor-text"
                     :class="{'bg-white border-zinc-300': editingSubtaskNoteId === subtask.id, 'hover:border-zinc-300': editingSubtaskNoteId !== subtask.id}"
                     @click.stop="startEditingSubtaskNote(subtask)"
                >
                  <div v-if="editingSubtaskNoteId === subtask.id" class="relative">
                     <textarea 
                       :id="'note-input-' + subtask.id"
                       v-model="tempNoteContent"
                       @blur="saveSubtaskNote(subtask)"
                       @keydown.enter.meta="saveSubtaskNote(subtask)"
                       @click.stop
                       class="w-full bg-transparent border-none p-0 text-xs focus:ring-0 focus:outline-none resize-none min-h-[60px] text-zinc-900 placeholder:text-muted-foreground"
                       placeholder="输入备注..."
                     ></textarea>
                  </div>
                  <div v-else>
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
                </div>

                <!-- Subtask Times (Buttons) -->
                <div class="ml-6 mt-2 grid grid-cols-2 gap-2">
                  <button 
                    @click.stop="openSubtaskTimeDialog(subtask, 'start', $event)"
                    class="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md border transition-colors text-xs font-medium w-full"
                    :class="subtask.start_time ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' : 'bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50 shadow-sm'"
                    title="开始时间"
                  >
                    <Clock class="h-3.5 w-3.5" />
                    <span>{{ subtask.start_time ? subtask.start_time.split(' ')[1].slice(0,5) : '开始' }}</span>
                  </button>
                  <button 
                    @click.stop="openSubtaskTimeDialog(subtask, 'completed', $event)"
                    class="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md border transition-colors text-xs font-medium w-full"
                    :class="subtask.completed_at ? 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100' : 'bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50 shadow-sm'"
                    title="完成时间"
                  >
                     <CheckCircle class="h-3.5 w-3.5" />
                     <span>{{ subtask.completed_at ? subtask.completed_at.split(' ')[1].slice(0,5) : '完成' }}</span>
                  </button>
                </div>

                <!-- Subtask Attachments (Manager Button) -->
                <div v-if="subtask.attachments && subtask.attachments.length > 0" class="ml-6 mt-2">
                   <Button 
                     variant="outline" 
                     size="sm" 
                     class="w-full h-auto py-1.5 text-xs font-medium gap-1.5 px-3 bg-white border-zinc-200 hover:bg-zinc-50 shadow-sm justify-center"
                     @click.stop="openAttachmentManager(subtask)"
                   >
                     <Paperclip class="h-3.5 w-3.5" />
                     <span>附件 ({{ subtask.attachments.length }})</span>
                   </Button>
                </div>
              </div>
            </div>
          </div>
          </Transition>

          <!-- Chart removed -->

          <!-- Card Footer -->
          <div class="p-4 pt-2 mt-auto">
            <div class="flex items-center justify-between text-xs text-muted-foreground border-t pt-3">
              <div class="space-y-1">
                <div v-if="memo.completed_at" class="flex items-center gap-2 text-green-600" title="完成时间">
                  <CheckCircle class="h-3 w-3" />
                  <span>{{ formatDate(memo.completed_at) }}</span>
                </div>
                <!-- Only show remaining time in footer if completed or no deadline (fallback) -->
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
      </div>

      <ConsumablesManager v-else-if="currentTab === 'consumables'" key="consumables" :active-filter="currentConsumableFilter" />
      </Transition>
        </div>
      </main>
    </div>

    <!-- Floating Action Button (Moved to Header, so removed from here or kept for mobile?) -->
    <!-- Keeping logic for consistency but hiding if layout changes handled it -->
    
    <!-- Attachment Manager Dialog -->
    <DialogRoot v-model:open="attachmentManagerOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[80] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent :style="dialogOriginStyle" class="fixed left-[50%] top-[50%] z-[80] grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg text-zinc-950">
          <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
            附件管理
          </DialogTitle>
          <div class="py-4 space-y-3 max-h-[60vh] overflow-y-auto">
             <div v-if="currentManagerSubtask && currentManagerSubtask.attachments && currentManagerSubtask.attachments.length > 0" class="grid gap-3">
               <div v-for="att in currentManagerSubtask.attachments" :key="att.id" class="flex items-center justify-between p-3 rounded-lg border border-zinc-200 bg-white">
                 <div class="flex items-center gap-3 min-w-0">
                   <div class="h-10 w-10 rounded-lg bg-zinc-100 flex items-center justify-center shrink-0">
                     <Paperclip class="h-5 w-5 text-zinc-500" />
                   </div>
                   <div class="min-w-0">
                     <p class="text-sm font-medium truncate" :title="att.filename">{{ att.filename }}</p>
                     <a :href="getAttachmentUrl(att.file_path)" target="_blank" class="inline-flex items-center justify-center gap-1 rounded-md text-xs font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-7 px-2 mt-1">
                       <Eye class="h-3 w-3" />
                       查看
                     </a>
                   </div>
                 </div>
                 <div class="flex items-center gap-1 shrink-0">
                   <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500 hover:text-zinc-900" @click="renameAttachment(att)">
                     <Edit2 class="h-4 w-4" />
                   </Button>
                   <Button variant="ghost" size="icon" class="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50" @click="deleteAttachment(att, currentManagerSubtask)">
                     <Trash2 class="h-4 w-4" />
                   </Button>
                 </div>
               </div>
             </div>
             <div v-else class="text-center py-8 text-muted-foreground">
               暂无附件
             </div>
          </div>
          <div class="flex justify-end">
            <Button variant="outline" @click="attachmentManagerOpen = false" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100">
              关闭
            </Button>
          </div>
          <DialogClose class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground text-zinc-500 hover:text-zinc-900">
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- Rename Attachment Dialog -->
    <DialogRoot v-model:open="renameDialogVisible">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[70] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent :style="dialogOriginStyle" class="fixed left-[50%] top-[50%] z-[70] grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg text-zinc-950">
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

    <!-- Category Choice Dialog -->
    <DialogRoot v-model:open="categoryChoiceOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[60] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent 
          :style="dialogOriginStyle"
          class="fixed left-[50%] top-[50%] z-[60] grid w-[calc(100%-2rem)] max-w-sm translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=open]:zoom-in-0 data-[state=closed]:zoom-out-0 sm:rounded-lg text-zinc-950"
        >
          <DialogTitle class="text-lg font-semibold text-center">
            选择备忘录类型
          </DialogTitle>
          <div class="grid grid-cols-2 gap-4 py-4">
            <button @click="handleCategorySelect('work', $event)" class="flex flex-col items-center justify-center p-4 border rounded-lg hover:bg-zinc-50 hover:border-zinc-900 transition-all gap-2 group">
               <div class="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                 <Briefcase class="h-6 w-6 text-yellow-700" />
               </div>
               <span class="font-medium text-zinc-900">工作</span>
            </button>
            <button @click="handleCategorySelect('life', $event)" class="flex flex-col items-center justify-center p-4 border rounded-lg hover:bg-zinc-50 hover:border-zinc-900 transition-all gap-2 group">
               <div class="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                 <Coffee class="h-6 w-6 text-green-700" />
               </div>
               <span class="font-medium text-zinc-900">生活</span>
            </button>
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
        <DialogOverlay class="fixed inset-0 z-[70] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent 
          :style="dialogOriginStyle"
          class="fixed z-[70] grid gap-4 bg-white shadow-lg duration-300 ease-out w-full h-[100dvh] top-0 left-0 border-0 p-4 overflow-y-auto data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=open]:zoom-in-0 data-[state=closed]:zoom-out-0 sm:fixed sm:left-[50%] sm:top-[50%] sm:h-auto sm:max-h-[90vh] sm:w-full sm:max-w-3xl sm:translate-x-[-50%] sm:translate-y-[-50%] sm:border sm:rounded-lg sm:p-6 sm:data-[state=closed]:zoom-out-0 sm:data-[state=open]:zoom-in-0 text-zinc-950"
        >
          <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
            {{ isEdit ? '编辑备忘' : '新建备忘' }}
          </DialogTitle>
          
          <input type="file" ref="fileInput" class="hidden" @change="handleFileChange" />
          
          <div class="grid gap-4 py-4">
            <!-- Category Selection Removed -->

            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">创建时间</label>
              <button 
                type="button"
                @click="openTimePicker('created_at', $event)"
                class="flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-left"
              >
                <span>{{ form.created_at_local ? form.created_at_local.replace('T', ' ').substring(0, 16) : '选择时间' }}</span>
                <CalendarIcon class="h-4 w-4 opacity-50" />
              </button>
            </div>



            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">标题</label>
              <Input v-model="form.title" placeholder="输入标题" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium leading-none">内容</label>
              <textarea 
                v-model="form.content" 
                class="flex min-h-[80px] w-full rounded-md border border-input bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-zinc-950 border-zinc-200"
                placeholder="输入内容"
              ></textarea>
            </div>
            
            <!-- Subtasks Section -->
            <div class="grid gap-2">
               <div class="flex justify-between items-center">
                 <label class="text-sm font-medium leading-none">子待办事项</label>
                 <div class="flex items-center gap-2">
                   <Button 
                      v-if="canUndo" 
                      size="sm" 
                      variant="ghost" 
                      @click="undo" 
                      type="button"
                      class="h-8 w-8 p-0 hover:bg-zinc-100 rounded-full"
                      title="撤销"
                    >
                      <Undo class="h-4 w-4 text-zinc-500" />
                    </Button>
                   <Button size="sm" variant="outline" @click="addSubTask" type="button" class="h-8 text-xs px-3 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 rounded-lg">
                     <Plus class="h-4 w-4 mr-1" /> 添加
                   </Button>
                 </div>
               </div>
               <draggable 
                 v-model="form.subtasks" 
                 :item-key="element => element.id || element._tempId"
                 handle=".drag-handle"
                 class="space-y-2 max-h-[300px] overflow-y-auto pr-1"
                 :animation="200"
                 ghost-class="ghost"
                 drag-class="drag"
                 @start="onDragStart"
               >
                 <template #item="{ element: subtask, index }">
                   <div 
                     class="flex items-center gap-2 group bg-white p-2 rounded-md border border-transparent hover:border-zinc-100 transition-colors"
                   >
                      <div class="drag-handle cursor-grab active:cursor-grabbing text-zinc-400 hover:text-zinc-600 p-2 shrink-0">
                        <GripVertical class="h-5 w-5" />
                      </div>
                      <Checkbox 
                        v-model:checked="subtask.is_completed" 
                        class="border-zinc-400 data-[state=checked]:bg-zinc-900 data-[state=checked]:text-zinc-50 shrink-0 h-5 w-5" 
                      />
                      
                      <!-- Content Area -->
                      <div class="flex-1 min-w-0">
                        <Input 
                          v-if="editingSubtaskId === (subtask.id || subtask._tempId)"
                          v-model="subtask.content" 
                          :data-subtask-id="subtask.id || subtask._tempId"
                          class="h-9 text-sm bg-white text-zinc-950 border-zinc-200" 
                          placeholder="待办事项内容"
                          @blur="finishEditingSubtask"
                          @keydown.enter="finishEditingSubtask"
                        />
                        <div 
                          v-else
                          class="text-sm py-1.5 px-2 truncate cursor-pointer select-none hover:bg-zinc-50 rounded"
                          :class="{'text-muted-foreground line-through': subtask.is_completed}"
                          @dblclick="startEditingSubtask(subtask)"
                          @touchstart="handleTouchStart(subtask)"
                          @touchend="handleTouchEnd"
                          @touchmove="handleTouchEnd"
                          @touchcancel="handleTouchEnd"
                          title="双击或长按编辑"
                        >
                          {{ subtask.content || '（无内容）' }}
                        </div>
                      </div>

                      <Button variant="ghost" size="icon" type="button" class="h-8 w-8 text-zinc-400 hover:text-destructive hover:bg-destructive/10 rounded-full shrink-0" @click="removeSubTask(index)">
                        <Trash2 class="h-4 w-4" />
                      </Button>
                   </div>
                 </template>
               </draggable>
               <div v-if="form.subtasks.length === 0" class="text-xs text-muted-foreground text-center py-4 bg-zinc-50 rounded-md border border-dashed border-zinc-200">
                 暂无子待办，点击上方"+"添加
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
            
          </div>
          <div class="flex flex-col gap-3 mt-6">
            <div class="flex justify-between items-center w-full" v-if="isEdit">
               <Button variant="ghost" size="icon" @click="handleDelete(currentId)" class="h-10 w-10 text-destructive hover:bg-destructive/10 rounded-full shrink-0" title="删除">
                 <Trash2 class="h-5 w-5" />
               </Button>
               <Button variant="outline" @click="saveAsTemplate" class="h-10 px-4 text-[clamp(12px,2vw,14px)] gap-2 border-dashed rounded-lg whitespace-nowrap shrink-0">
                 <Copy class="h-4 w-4" /> 存为模板
               </Button>
            </div>
            
            <div class="flex gap-3 w-full">
              <Button variant="outline" @click="dialogVisible = false" class="flex-1 h-10 px-6 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 rounded-lg text-[clamp(12px,2vw,14px)] whitespace-nowrap shrink-0">取消</Button>
              <Button @click="handleSubmit" class="flex-1 h-10 px-6 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 rounded-lg text-[clamp(12px,2vw,14px)] whitespace-nowrap shrink-0">确定</Button>
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
      <AlertDialogContent :style="dialogOriginStyle" class="w-[calc(100%-2rem)] max-w-lg gap-6 border bg-white p-6 shadow-lg rounded-lg md:w-full">
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
            class="rounded-lg font-medium bg-white text-zinc-950 border border-zinc-200 hover:bg-zinc-100 h-11 px-6 mt-0 whitespace-nowrap text-[clamp(12px,4vw,1rem)]"
          >
            {{ alertState.cancelText || '取消' }}
          </AlertDialogCancel>
          <AlertDialogAction 
            @click="onAlertConfirm" 
            class="rounded-lg font-medium bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 h-11 px-6 whitespace-nowrap text-[clamp(12px,4vw,1rem)]"
          >
            {{ alertState.confirmText || '确定' }}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <!-- Templates Dialog -->
    <DialogRoot v-model:open="templatesVisible">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent 
          :style="dialogOriginStyle"
          class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg sm:rounded-lg max-h-[85vh] overflow-y-auto text-zinc-950 duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=open]:zoom-in-0 data-[state=closed]:zoom-out-0"
        >
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
                   <Button size="sm" variant="secondary" class="h-9 px-3 text-xs rounded-lg" @click="useTemplate(temp, $event)">
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

    <!-- Subtask Time Dialog -->
    <DialogRoot v-model:open="subtaskTimeDialogOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[80] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent :style="dialogOriginStyle" class="fixed left-[50%] top-[50%] z-[80] grid w-full max-w-sm translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 rounded-lg">
          <div class="flex flex-col space-y-1.5 text-center sm:text-left">
            <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
              {{ subtaskTimeEditState.type === 'start' ? '开始时间' : '完成时间' }}
            </DialogTitle>
          </div>
          
          <div class="py-2">
            <DateTimeWheelPicker 
              v-model="subtaskTimeEditState.time" 
              mode="datetime"
              class="w-full"
            />
          </div>

          <div class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 gap-2">
            <Button variant="outline" @click="subtaskTimeDialogOpen = false">取消</Button>
            <Button @click="saveSubtaskTime">保存</Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- General Time Picker Dialog -->
    <DialogRoot v-model:open="timePickerOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-[80] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent :style="dialogOriginStyle" class="fixed left-[50%] top-[50%] z-[80] grid w-full max-w-sm translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 rounded-lg">
          <div class="flex flex-col space-y-1.5 text-center sm:text-left">
            <DialogTitle class="text-lg font-semibold leading-none tracking-tight">
              选择时间
            </DialogTitle>
          </div>
          
          <div class="py-2">
            <DateTimeWheelPicker 
              v-model="tempTimeValue" 
              mode="datetime"
              class="w-full"
            />
          </div>

          <div class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 gap-2">
            <Button variant="outline" @click="timePickerOpen = false">取消</Button>
            <Button @click="confirmTimePick">确定</Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
    <!-- End of General Time Picker Dialog -->

    <!-- Mobile Bottom Navigation -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white border-t border-zinc-200 flex items-center justify-around z-40 pb-[env(safe-area-inset-bottom)]">
       <template v-if="currentTab === 'memos'">
         <button 
           v-for="cat in ['all', 'work', 'life']" 
           :key="cat"
           @click="currentCategory = cat"
           class="flex flex-col items-center justify-center gap-1 w-full h-full"
           :class="currentCategory === cat ? 'text-zinc-900' : 'text-zinc-400 hover:text-zinc-600'"
         >
           <div class="h-1 w-12 rounded-full mb-1" :class="currentCategory === cat ? 'bg-zinc-900' : 'bg-transparent'"></div>
           <span class="text-sm font-medium">{{ cat === 'all' ? '全部' : (cat === 'work' ? '工作' : '生活') }}</span>
         </button>
       </template>
       <template v-else>
         <button 
           v-for="cat in ['全部', '车', '家', '食物']" 
           :key="cat"
           @click="currentConsumableFilter = cat"
           class="flex flex-col items-center justify-center gap-1 w-full h-full"
           :class="currentConsumableFilter === cat ? 'text-zinc-900' : 'text-zinc-400 hover:text-zinc-600'"
         >
           <div class="h-1 w-12 rounded-full mb-1" :class="currentConsumableFilter === cat ? 'bg-zinc-900' : 'bg-transparent'"></div>
           <span class="text-sm font-medium">{{ cat }}</span>
         </button>
       </template>
    </nav>

    <!-- Mobile FAB -->
    <button 
      v-if="currentTab === 'memos'"
      @click="openDialog($event)"
      class="md:hidden fixed bottom-28 right-6 h-14 w-14 bg-zinc-900 text-white rounded-full shadow-lg flex items-center justify-center z-40 hover:bg-zinc-800 transition-colors"
    >
      <Plus class="h-6 w-6" />
    </button>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue';
import { useInfiniteScroll, useSwipe } from '@vueuse/core';
import api from './api';
import { ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import ConsumablesManager from '@/components/ConsumablesManager.vue';
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
import DateTimeWheelPicker from '@/components/DateTimeWheelPicker.vue';
import { Plus, Trash2, Edit, Edit2, ExternalLink, CheckCircle, Clock, ChevronDown, ChevronUp, GripVertical, MessageSquare, X, LayoutTemplate, Copy, Paperclip, Pencil, Calendar as CalendarIcon, Eye, Undo, Menu, Briefcase, Coffee } from 'lucide-vue-next';
import draggable from 'vuedraggable';

// State
const memos = ref([]);
const loading = ref(false);
const page = ref(0);
const hasMore = ref(true);
const dialogVisible = ref(false);
const categoryChoiceOpen = ref(false);
const isEdit = ref(false);
const currentId = ref(null);
const dialogOriginStyle = ref({ transformOrigin: 'center' });

// Transition Hooks for Smooth Subtask Expansion
const onExpandEnter = (el) => {
  el.style.height = '0';
  el.style.opacity = '0';
  el.style.overflow = 'hidden';
  // Force reflow
  void el.offsetHeight; 
  el.style.transition = 'height 0.8s cubic-bezier(0.25, 0.1, 0.25, 1.0), opacity 0.8s ease-in';
  el.style.height = el.scrollHeight + 'px';
  el.style.opacity = '1';
};

const onExpandAfterEnter = (el) => {
  el.style.height = 'auto';
  el.style.overflow = 'visible';
};

const onExpandLeave = (el) => {
  el.style.height = el.scrollHeight + 'px';
  el.style.opacity = '1';
  el.style.overflow = 'hidden';
  // Force reflow
  void el.offsetHeight;
  el.style.transition = 'height 0.8s cubic-bezier(0.25, 0.1, 0.25, 1.0), opacity 0.8s ease-out';
  el.style.height = '0';
  el.style.opacity = '0';
};

const updateTransformOrigin = (event) => {
  if (!event || !event.clientX) {
    dialogOriginStyle.value = { transformOrigin: 'center' };
    return;
  }
  const x = event.clientX - window.innerWidth / 2;
  const y = event.clientY - window.innerHeight / 2;
  dialogOriginStyle.value = { 
    transformOrigin: `calc(50% + ${x}px) calc(50% + ${y}px)` 
  };
};
const currentTab = ref('memos'); // 'memos' | 'consumables'
const currentCategory = ref('all'); // 'all', 'work', 'life'
const currentConsumableFilter = ref('全部'); // '全部', '家', '车', '食物'
const templates = ref([]);
const templatesVisible = ref(false);
const attachmentManagerOpen = ref(false);
const mobileMenuOpen = ref(false);
const currentManagerSubtask = ref(null);
const templateSearchQuery = ref('');

// Swipe Navigation
const containerRef = ref(null);
const { direction, isSwiping, lengthX } = useSwipe(containerRef);

watch(isSwiping, (newVal) => {
  if (!newVal) { // Swiping ended
    const threshold = 50; // Minimum distance
    if (Math.abs(lengthX.value) > threshold) {
      if (currentTab.value === 'memos') {
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
      } else if (currentTab.value === 'consumables') {
        const categories = ['全部', '车', '家', '食物'];
        const currentIndex = categories.indexOf(currentConsumableFilter.value);
        
        if (direction.value === 'left') {
          if (currentIndex < categories.length - 1) {
            currentConsumableFilter.value = categories[currentIndex + 1];
          }
        } else if (direction.value === 'right') {
          if (currentIndex > 0) {
            currentConsumableFilter.value = categories[currentIndex - 1];
          }
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
  created_at_local: null,
  completed_at_local: null,
  subtasks: [],
  category: 'work'
});

// Helper to format date
// Removed time-related helpers


// Fetch memos
const fetchMemos = async (isLoadMore = false) => {
  if (loading.value) return;
  if (!isLoadMore) {
    page.value = 0;
    // memos.value = []; // Commented out to enable smooth transition
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
      _showSubtasks: false,
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
const useTemplate = (template, event) => {
  updateTransformOrigin(event);
  form.value = {
    title: template.title,
    content: template.content,
    isCompleted: false,
    subtasks: template.subtasks.map(st => ({
      ...st,
      id: undefined, // Clear ID for new subtasks
      is_completed: false,
      showNote: false,
      note: ''
    })),
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
const openDialog = (event) => {
  updateTransformOrigin(event);
  categoryChoiceOpen.value = true;
};

const handleCategorySelect = async (category, event) => {
  updateTransformOrigin(event);
  categoryChoiceOpen.value = false;
  
  isEdit.value = false;
  currentId.value = null;
  form.value = {
    title: '',
    content: '',
    isCompleted: false,
    created_at_local: new Date().toISOString(),
    completed_at_local: null,
    deadline_local: null,
    subtasks: [],
    category: category
  };

  // Check for templates (matching category)
  const hasTemplates = templates.value.some(t => t.category === category);
  
  if (hasTemplates) {
     if (await showConfirm('是否使用已有模板？', '新建备忘', '使用模板', '直接创建')) {
        templatesVisible.value = true;
        return;
     }
  }
  
  dialogVisible.value = true;
};

const openEditDialog = (memo, event) => {
  updateTransformOrigin(event);
  isEdit.value = true;
  currentId.value = memo.id;
  form.value = {
    title: memo.title,
    content: memo.content,
    isCompleted: !!memo.completed_at,
    created_at_local: memo.created_at,
    completed_at_local: memo.completed_at,
    deadline_local: memo.deadline,
    subtasks: memo.subtasks ? memo.subtasks.map(st => ({
      ...st,
      showNote: !!st.note
    })) : [],
    category: memo.category || 'work'
  };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  await nextTick(); // Ensure any blur events have fired
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      category: form.value.category,
      created_at: form.value.created_at_local,
      deadline: form.value.deadline_local,
      subtasks: form.value.subtasks.map(st => ({
          id: st.id, // Keep ID if exists
          content: st.content,
          note: st.note,
          is_completed: st.is_completed,
          created_at: null,
          start_time: null,
          completed_at: null
        }))
    };

    if (isEdit.value && form.value.isCompleted) {
       payload.completed_at = form.value.completed_at_local || new Date().toISOString();
    } else if (isEdit.value && !form.value.isCompleted) {
       payload.completed_at = null;
    } else if (!isEdit.value && form.value.isCompleted) {
       payload.completed_at = form.value.completed_at_local || new Date().toISOString();
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

// Inline Note Editing
const editingSubtaskNoteId = ref(null);
const tempNoteContent = ref('');

const startEditingSubtaskNote = (subtask) => {
  editingSubtaskNoteId.value = subtask.id;
  tempNoteContent.value = subtask.note || '';
  nextTick(() => {
    const el = document.getElementById(`note-input-${subtask.id}`);
    if (el) el.focus();
  });
};

const saveSubtaskNote = async (subtask) => {
  if (editingSubtaskNoteId.value !== subtask.id) return;
  
  const oldNote = subtask.note;
  const newNote = tempNoteContent.value;
  
  // Optimistic update
  subtask.note = newNote;
  editingSubtaskNoteId.value = null;
  
  if (oldNote !== newNote) {
    try {
      await api.put(`/subtasks/${subtask.id}`, {
        content: subtask.content,
        note: newNote,
        is_completed: subtask.is_completed
      });
    } catch (error) {
      console.error('Failed to update subtask note:', error);
      subtask.note = oldNote;
      showAlert('更新备注失败');
    }
  }
};

// Subtask Time Editing
const subtaskTimeDialogOpen = ref(false);
const subtaskTimeEditState = ref({
  subtask: null,
  type: 'start', // 'start' | 'completed'
  time: ''
});

const getRemainingTime = (deadline) => {
  if (!deadline) return '';
  const end = new Date(deadline.replace(' ', 'T'));
  const now = new Date();
  const diff = end - now;
  
  if (diff < 0) return '已过期';
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  
  if (days > 0) return `剩余：${days}天 ${hours}小时`;
  return `剩余：${hours}小时`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr.replace(' ', 'T'));
  const m = (date.getMonth() + 1).toString().padStart(2, '0');
  const d = date.getDate().toString().padStart(2, '0');
  const h = date.getHours().toString().padStart(2, '0');
  const min = date.getMinutes().toString().padStart(2, '0');
  return `${m}-${d} ${h}:${min}`;
};

const getSubtaskDuration = (subtask) => {
  if (!subtask.start_time || !subtask.completed_at) return '';
  const start = new Date(subtask.start_time.replace(' ', 'T'));
  const end = new Date(subtask.completed_at.replace(' ', 'T'));
  const diff = end - start;
  
  if (diff < 0) return '-';
  
  const minutes = Math.floor(diff / (1000 * 60));
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
};

const openSubtaskTimeDialog = (subtask, type, event) => {
  updateTransformOrigin(event);
  let timeVal = type === 'start' ? subtask.start_time : subtask.completed_at;
  // Convert "YYYY-MM-DD HH:MM" to "YYYY-MM-DDTHH:MM" for safer parsing by Date constructor
  if (timeVal && timeVal.includes(' ')) {
      timeVal = timeVal.replace(' ', 'T');
  }
  subtaskTimeEditState.value = {
    subtask,
    type,
    time: timeVal
  };
  subtaskTimeDialogOpen.value = true;
};

// General Time Picker Logic
const timePickerOpen = ref(false);
const tempTimeValue = ref('');
const timePickerTarget = ref(''); // 'created_at' | 'deadline' | 'single_memo_deadline'
const updatingMemo = ref(null);

const openMemoDeadlinePicker = (memo, event) => {
  if (isDeadlineLongPress) {
    isDeadlineLongPress = false;
    return;
  }
  updateTransformOrigin(event);
  updatingMemo.value = memo;
  timePickerTarget.value = 'single_memo_deadline';
  
  let val = memo.deadline;
  if (val && val.includes(' ')) {
      val = val.replace(' ', 'T');
  }
  
  tempTimeValue.value = val || new Date().toISOString();
  timePickerOpen.value = true;
};

const openTimePicker = (target, event) => {
  if (event) updateTransformOrigin(event);
  timePickerTarget.value = target;
  let val = target === 'created_at' ? form.value.created_at_local : form.value.deadline_local;
  
  if (val && val.includes(' ')) {
      val = val.replace(' ', 'T');
  }
  
  tempTimeValue.value = val || new Date().toISOString();
  timePickerOpen.value = true;
};

const confirmTimePick = async () => {
  if (timePickerTarget.value === 'created_at') {
    form.value.created_at_local = tempTimeValue.value;
  } else if (timePickerTarget.value === 'deadline') {
    form.value.deadline_local = tempTimeValue.value;
  } else if (timePickerTarget.value === 'single_memo_deadline') {
    if (updatingMemo.value) {
      try {
         const newDeadline = tempTimeValue.value.replace('T', ' ');
         // Optimistic update
         updatingMemo.value.deadline = newDeadline;
         
         await api.put(`/memos/${updatingMemo.value.id}`, {
            deadline: newDeadline
         });
         await fetchMemos();
      } catch (e) {
         console.error(e);
         showAlert('更新截止日期失败');
         fetchMemos(); // Revert
      }
    }
    updatingMemo.value = null;
  }
  timePickerOpen.value = false;
};

const saveSubtaskTime = async () => {
  const { subtask, type, time } = subtaskTimeEditState.value;
  if (!subtask) return;
  
  // Validation: Ensure completed_at > start_time
  if (type === 'completed' && time && subtask.start_time) {
     const start = new Date(subtask.start_time.replace(' ', 'T'));
     const end = new Date(time.replace(' ', 'T'));
     if (end <= start) {
        showAlert('完成时间必须晚于开始时间');
        return;
     }
  } else if (type === 'start' && time && subtask.completed_at) {
     const start = new Date(time.replace(' ', 'T'));
     const end = new Date(subtask.completed_at.replace(' ', 'T'));
     if (start >= end) {
        showAlert('开始时间必须早于完成时间');
        return;
     }
  }

  try {
    const payload = {};
    if (type === 'start') {
      payload.start_time = time;
    } else {
      payload.completed_at = time;
      // If setting completed time, ensure is_completed is true
      if (time) payload.is_completed = true;
    }
    
    await api.put(`/subtasks/${subtask.id}`, payload);
    await fetchMemos();
    subtaskTimeDialogOpen.value = false;
  } catch (error) {
    console.error('Failed to update subtask time:', error);
    showAlert('更新时间失败');
  }
};

const handleDelete = async (id) => {
  if (!await showConfirm('确定删除该备忘录吗？')) return;
  try {
    await api.delete(`/memos/${id}`);
    dialogVisible.value = false;
    fetchMemos();
  } catch (error) {
    console.error('Failed to delete memo:', error);
  }
};

const handleStatusChange = (checked) => {
  if (checked) {
    if (!form.value.completed_at_local) {
      form.value.completed_at_local = new Date().toISOString();
    }
  } else {
    form.value.completed_at_local = null;
  }
};

const addSubTask = () => {
  saveHistory();
  const newSubtask = {
    content: '',
    is_completed: false,
    _tempId: Date.now() + Math.random().toString(36).substr(2, 9) // Temporary ID for keying
  };
  form.value.subtasks.push(newSubtask);
  
  // Auto enter edit mode
  startEditingSubtask(newSubtask);
};

const removeSubTask = async (index) => {
  if (!await showConfirm('确定删除该子待办事项吗？')) return;
  saveHistory();
  form.value.subtasks.splice(index, 1);
};

// Subtask History & Editing
const subtaskHistory = ref([]);
const editingSubtaskId = ref(null);

const saveHistory = () => {
  // Limit history to 20 steps
  if (subtaskHistory.value.length >= 20) {
    subtaskHistory.value.shift();
  }
  subtaskHistory.value.push(JSON.parse(JSON.stringify(form.value.subtasks)));
};

const undo = () => {
  if (subtaskHistory.value.length === 0) return;
  const previousState = subtaskHistory.value.pop();
  form.value.subtasks = previousState;
};

const canUndo = computed(() => subtaskHistory.value.length > 0);

const startEditingSubtask = (subtask) => {
  // Save history before editing starts to allow undoing the rename
  // Check if we just added this task (history might already be saved by addSubTask)
  // But saving again is fine, it just adds a granular step
  saveHistory();
  
  editingSubtaskId.value = subtask.id || subtask._tempId;
  nextTick(() => {
    const el = document.querySelector(`input[data-subtask-id="${editingSubtaskId.value}"]`);
    if (el) el.focus();
  });
};

const finishEditingSubtask = () => {
  editingSubtaskId.value = null;
};

// Handle drag end for history
const onDragEnd = () => {
  // We save history BEFORE drag starts usually, but vuedraggable modifies array in place.
  // To support undoing reorder, we should verify how to capture state.
  // Actually, easiest is to save history on @start
};
const onDragStart = () => {
  saveHistory();
};

let touchTimer = null;
const handleTouchStart = (subtask) => {
  touchTimer = setTimeout(() => {
    startEditingSubtask(subtask);
  }, 500);
};
const handleTouchEnd = () => {
  if (touchTimer) clearTimeout(touchTimer);
};

let deadlineTouchTimer = null;
let isDeadlineLongPress = false;

const handleDeadlineTouchStart = (memo) => {
  isDeadlineLongPress = false;
  deadlineTouchTimer = setTimeout(async () => {
    isDeadlineLongPress = true;
    if (await showConfirm('确定清除该备忘录的截止日期吗？')) {
      try {
        await api.put(`/memos/${memo.id}`, {
          deadline: null
        });
        await fetchMemos();
      } catch (e) {
        console.error(e);
        showAlert('清除截止日期失败');
      }
    }
  }, 500);
};

const handleDeadlineTouchEnd = () => {
  if (deadlineTouchTimer) clearTimeout(deadlineTouchTimer);
};

// Attachment handling
const fileInput = ref(null);
const currentSubtaskForUpload = ref(null);
const renameDialogVisible = ref(false);
const renameForm = ref({
  attachment: null,
  newName: ''
});

const openAttachmentManager = (subtask) => {
  currentManagerSubtask.value = subtask;
  attachmentManagerOpen.value = true;
};

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
  if (!path) return '';
  // If path contains backslashes (Windows), replace with forward slashes
  const normalizedPath = path.replace(/\\/g, '/');
  return `${api.defaults.baseURL}/${normalizedPath}`;
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
