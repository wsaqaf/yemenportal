require "matrix"

class PostsClusterizer::RelatedPostsFinder
  def initialize(post)
    @post = post
  end

  def topic_with_related_posts_or_nil
    if posts.present? && related_post_found?
      most_similar_topic
    end
  end

  private

  attr_reader :post

  def related_post_found?
    similarity_value_of_most_similar_post > related_post_similarity_threshold
  end

  def similarity_value_of_most_similar_post
    similarity[0]
  end

  def similarity_post_id
    similarity[1]
  end

  def similarity
    @_similarity ||= similarity_matrix[0, 1..-1].each_with_index
      .reject do |(value, _index)|
        value > duplicate_post_similarity_threshold
      end
      .max
  end

  def most_similar_topic
    most_similar_post.main_topic || most_similar_post.topic
  end

  def most_similar_post
    @_most_similar_post ||= posts[similarity_post_id]
  end

  def posts
    @_posts ||= load_posts
  end

  def load_posts
    ::Post
      .not_for_source(post.source_id)
      .created_after_date(clustering_time_limit.hours.ago)
  end

  def related_post_similarity_threshold
    related_posts_finder_config["related_similarity_threshold"]
  end

  def duplicate_post_similarity_threshold
    related_posts_finder_config["duplicate_similarity_threshold"]
  end

  def clustering_time_limit
    related_posts_finder_config["clustering_time_limit"]
  end

  def related_posts_finder_config
    ::Rails.application.config_for(:related_posts_finder)
  end

  # Pretty heavy operation. Consider to cache it.
  # https://github.com/jpmckinney/tf-idf-similarity/issues/6
  def similarity_matrix
    tfidf_similarity_model.similarity_matrix
  end

  def tfidf_similarity_model
    TfIdfSimilarity::TfIdfModel.new(documents)
  end

  def documents
    documents_from_posts.unshift(post_as_document)
  end

  def documents_from_posts
    posts.map do |post|
      PostsClusterizer::RelatedPostsFinder.new(post)
    end
  end

  def post_as_document
    PostsClusterizer::RelatedPostsFinder.new(post)
  end
end
