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
    post.topic = post_topic(post)
    if post.save
      @added_posts << post
    else
      source.update(state: Source.state.not_full_info)
    end
  end

  private

  def post_topic(post)
    if post.valid? && !duplicated_for_source?(post.description)
      TfIdfService.new(stemmed_text: post.stemmed_text).post_topic
    end
  end

  def duplicated_for_source?(description)
    Post.where(source: source, description: description).present?
  end

  def post_params(item)
    if source.source_type.rss?
      rss_params(item)
    elsif source.source_type.facebook?
      facebook_params(item)
    end
  end

  def rss_params(item)
    photo_tag = item.summary.slice!(IMG_TAG_REGEXP)
    photo_url = photo_tag.present? ? photo_tag.slice(URL_REGEXP) : nil
    { description: item.summary, link: item.url, published_at: item.published, source: source,
      title: item.title, photo_url: photo_url, stemmed_text: stemmed_text(item.summary, item.title) }
  end

  def facebook_params(item)
    message = item["message"] || item["name"]
    title = message.match(/[^\n\.]+/).to_s
    { description: message, link: item["link"], published_at: item["created_time"], source: source,
    title: title, photo_url: item["picture"],
    stemmed_text: stemmed_text(message, title) }
  end

  def stemmed_text(description = "", title = "")
    text = "#{title} #{description}"
    sanitize_description = ActionView::Base.full_sanitizer.sanitize(text)
    sanitize_description.split.map { |word| ArStemmer.stem(word) }.join(" ")
  end
end
