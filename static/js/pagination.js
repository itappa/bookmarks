document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowLeft') {
    // 前のページへのリンク要素を取得
    var prevLink = document.querySelector('a[aria-label="Previous"]');
    if (prevLink && !prevLink.getAttribute('href').includes('#')) {
      prevLink.click(); // 前のページへ移動
    }
  } else if (e.key === 'ArrowRight') {
    // 次のページへのリンク要素を取得
    var nextLink = document.querySelector('a[aria-label="Next"]');
    if (nextLink && !nextLink.getAttribute('href').includes('#')) {
      nextLink.click(); // 次のページへ移動
    }
  }
});