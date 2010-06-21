
#ifndef __BUFFER_CACHE_WRITEBACK_IMPL_HPP__
#define __BUFFER_CACHE_WRITEBACK_IMPL_HPP__

template <class config_t>
writeback_tmpl_t<config_t>::writeback_tmpl_t(serializer_t *_serializer)
    : serializer(_serializer) {
}

template <class config_t>
void writeback_tmpl_t<config_t>::start() {
    timespec ts;
    ts.tv_sec = 5; /* TODO(NNW): This should be a user-specified value. */
    ts.tv_nsec = 0;
    get_cpu_context()->event_queue->set_timer(&ts, timer_callback, this);
}

template <class config_t>
void writeback_tmpl_t<config_t>::buf_t::set_dirty(
        typename config_t::buf_t *super) {
    dirty = true;
    writeback->dirty_bufs.insert(super);
    writeback->txns.insert(super->get_transaction());
    //dirty_blocks.insert(block_id);
}

template <class config_t>
void writeback_tmpl_t<config_t>::timer_callback(void *ctx) {
    static_cast<writeback_tmpl_t *>(ctx)->writeback();
}

template <class config_t>
void writeback_tmpl_t<config_t>::writeback() {
    /* TODO(NNW): Implement. */
}

#endif  // __BUFFER_CACHE_WRITEBACK_IMPL_HPP__
