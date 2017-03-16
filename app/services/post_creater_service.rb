class PostCreaterService
  def self.add_post(item, source)
    post = Post.new(description: item.description, link: item.link, published_at: item.pubDate, source: source,
      title: item.title)
    post.categories = [source.category] if source.category.present?
    source.update(state: Source.state.incorrect_stucture) unless post.save
  end
end
