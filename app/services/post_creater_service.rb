class PostCreaterService
  def self.add_post(item, source)
    post = Post.new(description: item.description, link: item.link, published_at: item.pubDate, source: source,
      title: item.title)
    post.categories = [source.category] if source.category.present?
    post.save
  end
end
