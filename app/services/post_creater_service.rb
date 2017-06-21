class PostCreaterService
  IMG_TAG_REGEXP = %r{<img[^>]+\/>}
  URL_REGEXP = /(?<=src=(\"|\'))[^\"\']+/
  attr_accessor :added_posts
  attr_reader :source

  def initialize(source)
    @added_posts = []
    @source = source
  end

  def add_post(item)
    post = Post.new(post_params(item))
    post.state = :approved if source.whitelisted
    post.categories = [source.category] if source.category.present?
    post.topic = TfIdfService.new(description: post.stemmed_text).post_topic if post.valid?
    if post.save
      @added_posts << post
    else
      source.update(state: Source.state.not_full_info)
    end
  end

  private

  def post_params(item)
    if source.source_type.rss?
      photo_tag = item.summary.slice!(IMG_TAG_REGEXP)
      photo_url = photo_tag.present? ? photo_tag.slice(URL_REGEXP) : nil
      { description: item.summary, link: item.url, published_at: item.published, source: source,
        title: item.title, photo_url: photo_url, stemmed_text: stemmed_text(item.summary) }
    elsif source.source_type.facebook?
      message = item["message"] || item["name"]
      { description: message, link: item["link"], published_at: item["created_time"], source: source,
      title: message.match(/[^\n\.]+/).to_s, photo_url: item["picture"], stemmed_text: stemmed_text(message) }
    end
  end

  def stemmed_text(description = "")
    sanitize_description = ActionView::Base.full_sanitizer.sanitize(description)
    sanitize_description.split.map { |word| ArStemmer.stem(word) }.join(" ")
  end
end
