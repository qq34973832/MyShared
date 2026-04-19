from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional, Any
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础 CRUD 操作类"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """获取单条记录"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取多条记录"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """创建记录"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """更新记录"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """删除记录"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
